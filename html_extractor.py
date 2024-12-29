import re
import json
import os
import sys
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import errorcode
import db_config  # Importar db_config para la configuración de la base de datos
import social_api_helper  # Importar el nuevo módulo

def extract_info(file_path, db_config):
    # Verificar si el archivo existe
    if not os.path.isfile(file_path):
        print(f"El archivo {file_path} no existe.")
        return None

    # Leer el archivo HTML
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Usar BeautifulSoup para analizar el HTML
    soup = BeautifulSoup(content, 'html.parser')

    # Inicializar los contadores de seguidores
    Qfb_followers = 0
    Qig_followers = 0
    Qtw_followers = 0
    Qyt_followers = 0
    Qtik_followers = 0
    Qln_followers = 0

    # Extraer las URLs de redes sociales y otros enlaces
    social_links = {
        'facebook': [],
        'instagram': [],
        'meta': [],
        'twitter': [],
        'youtube': [],
        'tiktok': [],
        'linkedin': [],
        'whatsapp': [],
        'contact': []
    }

    whatsapp_patterns = [
        "wa.link", "api.whatsapp.com", "whatsapp://", "wa.me", "walink", "web.whatsapp.com"
    ]

    contact_patterns = [
        "contacto", "contact"
    ]

    for a in soup.find_all('a', href=True):
        url = a['href']
        if 'facebook' in url:
            social_links['facebook'].append(url)
        elif 'instagram' in url:
            social_links['instagram'].append(url)
        elif 'meta' in url:
            social_links['meta'].append(url)
        elif 'twitter' in url:
            social_links['twitter'].append(url)
        elif 'youtube' in url:
            social_links['youtube'].append(url)
        elif 'tiktok' in url:
            social_links['tiktok'].append(url)
        elif 'linkedin.com' in url:
            social_links['linkedin'].append(url)
        elif any(pattern in url for pattern in whatsapp_patterns):
            social_links['whatsapp'].append(url)
        elif any(pattern in url.lower() for pattern in contact_patterns):
            social_links['contact'].append(url)

    # Extraer teléfonos y correos electrónicos
    phones = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('tel:')]
    emails = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('mailto:')]

    # Obtener seguidores de cada red social
    if social_links['facebook']:
        Qfb_followers = social_api_helper.get_facebook_followers(social_links['facebook'][0])
    if social_links['instagram']:
        Qig_followers = social_api_helper.get_instagram_followers(social_links['instagram'][0])
    if social_links['twitter']:
        Qtw_followers = social_api_helper.get_twitter_followers(social_links['twitter'][0])
    if social_links['youtube']:
        Qyt_followers = social_api_helper.get_youtube_subscribers(social_links['youtube'][0])
    if social_links['tiktok']:
        Qtik_followers = social_api_helper.get_tiktok_followers(social_links['tiktok'][0])
    if social_links['linkedin']:
        Qln_followers = social_api_helper.get_linkedin_followers(social_links['linkedin'][0])

    # Imprimir las URLs de redes sociales extraídas
    print("Enlaces de redes sociales extraídos:")
    for key, links in social_links.items():
        print(f"{key}: {links}")

    # Imprimir teléfonos y correos electrónicos extraídos
    print(f"Teléfonos extraídos: {phones}")
    print(f"Correos electrónicos extraídos: {emails}")

    # Datos a almacenar
    place_id = os.path.basename(file_path).split('.')[0]  # Asumimos que el nombre del archivo es el place_id
    extracted_data = {
        'place_id': place_id,
        'facebook': bool(social_links['facebook']),
        'Qfb': Qfb_followers,
        'FBLink': json.dumps(social_links['facebook']),
        'instagram': bool(social_links['instagram']),
        'Qig': Qig_followers,
        'IGLink': json.dumps(social_links['instagram']),
        'meta': bool(social_links['meta']),
        'Qme': len(social_links['meta']),  # No obtenemos seguidores de Meta
        'MetaLink': json.dumps(social_links['meta']),
        'twitter': bool(social_links['twitter']),
        'Qtw': Qtw_followers,
        'TwitterLink': json.dumps(social_links['twitter']),
        'youtube': bool(social_links['youtube']),
        'Qyt': Qyt_followers,
        'YouTubeLink': json.dumps(social_links['youtube']),
        'tiktok': bool(social_links['tiktok']),
        'Qtik': Qtik_followers,
        'TikTokLink': json.dumps(social_links['tiktok']),
        'linkedin': bool(social_links['linkedin']),
        'Qln': Qln_followers,
        'LinkedInLink': json.dumps(social_links['linkedin']),
        'whatsapp': bool(social_links['whatsapp']),
        'Qwa': len(social_links['whatsapp']),  # No obtenemos seguidores de WhatsApp
        'WhatsAppLink': json.dumps(social_links['whatsapp']),
        'contact': bool(social_links['contact']),
        'Qct': len(social_links['contact']),
        'ContactLink': json.dumps(social_links['contact']),
        'phones': json.dumps(phones),
        'emails': json.dumps(emails)
    }

    # Conectar a la base de datos
    connection = None
    cursor = None
    try:
        connection, cursor = db_config.connect()

        # Crear la tabla si no existe (asegurarse de que las columnas Q* son del tipo adecuado)
        create_table_query = """
        CREATE TABLE IF NOT EXISTS extracted_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            place_id VARCHAR(255) NOT NULL UNIQUE,
            facebook BOOLEAN,
            Qfb INT,
            FBLink JSON,
            instagram BOOLEAN,
            Qig INT,
            IGLink JSON,
            meta BOOLEAN,
            Qme INT,
            MetaLink JSON,
            twitter BOOLEAN,
            Qtw INT,
            TwitterLink JSON,
            youtube BOOLEAN,
            Qyt INT,
            YouTubeLink JSON,
            tiktok BOOLEAN,
            Qtik INT,
            TikTokLink JSON,
            linkedin BOOLEAN,
            Qln INT,
            LinkedInLink JSON,
            phones JSON,
            emails JSON,
            whatsapp BOOLEAN,
            Qwa INT,
            WhatsAppLink JSON,
            contact BOOLEAN,
            Qct INT,
            ContactLink JSON,
            problems JSON,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)

        # Insertar o actualizar los datos extraídos en la tabla
        insert_query = """
        INSERT INTO extracted_info (place_id, facebook, Qfb, FBLink, instagram, Qig, IGLink, meta, Qme, MetaLink,
                                    twitter, Qtw, TwitterLink, youtube, Qyt, YouTubeLink, tiktok, Qtik, TikTokLink,
                                    linkedin, Qln, LinkedInLink, whatsapp, Qwa, WhatsAppLink, contact, Qct, ContactLink,
                                    phones, emails)
        VALUES (%(place_id)s, %(facebook)s, %(Qfb)s, %(FBLink)s, %(instagram)s, %(Qig)s, %(IGLink)s, %(meta)s, %(Qme)s, %(MetaLink)s,
                %(twitter)s, %(Qtw)s, %(TwitterLink)s, %(youtube)s, %(Qyt)s, %(YouTubeLink)s, %(tiktok)s, %(Qtik)s, %(TikTokLink)s,
                %(linkedin)s, %(Qln)s, %(LinkedInLink)s, %(whatsapp)s, %(Qwa)s, %(WhatsAppLink)s, %(contact)s, %(Qct)s, %(ContactLink)s,
                %(phones)s, %(emails)s)
        ON DUPLICATE KEY UPDATE
            facebook = VALUES(facebook),
            Qfb = VALUES(Qfb),
            FBLink = VALUES(FBLink),
            instagram = VALUES(instagram),
            Qig = VALUES(Qig),
            IGLink = VALUES(IGLink),
            meta = VALUES(meta),
            Qme = VALUES(Qme),
            MetaLink = VALUES(MetaLink),
            twitter = VALUES(twitter),
            Qtw = VALUES(Qtw),
            TwitterLink = VALUES(TwitterLink),
            youtube = VALUES(youtube),
            Qyt = VALUES(Qyt),
            YouTubeLink = VALUES(YouTubeLink),
            tiktok = VALUES(tiktok),
            Qtik = VALUES(Qtik),
            TikTokLink = VALUES(TikTokLink),
            linkedin = VALUES(linkedin),
            Qln = VALUES(Qln),
            LinkedInLink = VALUES(LinkedInLink),
            whatsapp = VALUES(whatsapp),
            Qwa = VALUES(Qwa),
            WhatsAppLink = VALUES(WhatsAppLink),
            contact = VALUES(contact),
            Qct = VALUES(Qct),
            ContactLink = VALUES(ContactLink),
            phones = VALUES(phones),
            emails = VALUES(emails)
        ;
        """
        cursor.execute(insert_query, extracted_data)
        connection.commit()

        print("Datos insertados o actualizados correctamente.")

        # Generar JSON con todos los datos encontrados
        json_datos = json.dumps(extracted_data, indent=4)
        print("JSON generado:", json_datos)
        return json_datos  # Devolver JSON generado

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error de autenticación.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de datos no existe.")
        else:
            print(err)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()