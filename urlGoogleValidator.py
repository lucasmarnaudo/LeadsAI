import sys
import json
import subprocess  # Importar subprocess para ejecutar scripts externos
from urllib.parse import urlparse
import db_config  # Importar db_config para la configuración de la base de datos
import mysql.connector

# Lista de dominios conocidos de redes sociales
KNOWN_DOMAINS = ["facebook.com", "fb.com", "instagram.com", "ig.com", "linkedin.com", "twitter.com", "t.co", "x.com", "tiktok.com"]

def insert_social_links(place_id, url):
    connection, cursor = db_config.connect()
    if not connection or not cursor:
        print("No se pudo conectar a la base de datos.")
        return

    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    print(f"Inserción en la base de datos para el dominio {domain}")

    extracted_data = {
        'place_id': place_id,
        'facebook': 1 if "facebook.com" in domain or "fb.com" in domain else 0,
        'Qfb': 1 if "facebook.com" in domain or "fb.com" in domain else 0,
        'FBLink': json.dumps([url]) if "facebook.com" in domain or "fb.com" in domain else '[]',
        'instagram': 1 if "instagram.com" in domain or "ig.com" in domain else 0,
        'Qig': 1 if "instagram.com" in domain or "ig.com" in domain else 0,
        'IGLink': json.dumps([url]) if "instagram.com" in domain or "ig.com" in domain else '[]',
        'meta': 0,
        'Qme': 0,
        'MetaLink': '[]',
        'twitter': 1 if "twitter.com" in domain or "x.com" in domain or "t.co" in domain else 0,
        'Qtw': 1 if "twitter.com" in domain or "x.com" in domain or "t.co" in domain else 0,
        'TwitterLink': json.dumps([url]) if "twitter.com" in domain or "x.com" in domain or "t.co" in domain else '[]',
        'youtube': 0,
        'Qyt': 0,
        'YouTubeLink': '[]',
        'tiktok': 1 if "tiktok.com" in domain else 0,
        'Qtik': 1 if "tiktok.com" in domain else 0,
        'TikTokLink': json.dumps([url]) if "tiktok.com" in domain else '[]',
        'linkedin': 1 if "linkedin.com" in domain else 0,
        'Qln': 1 if "linkedin.com" in domain else 0,
        'LinkedInLink': json.dumps([url]) if "linkedin.com" in domain else '[]',
        'phones': '[]',
        'emails': '[]',
        'whatsapp': 0,
        'Qwa': 0,
        'WhatsAppLink': '[]',
        'contact': 0,
        'Qct': 0,
        'ContactLink': '[]'
    }

    try:
        # Crear la tabla si no existe
        create_table_query = """
        CREATE TABLE IF NOT EXISTS extracted_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            place_id VARCHAR(255) NOT NULL,
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
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)

        # Insertar los datos extraídos en la tabla
        insert_query = """
        INSERT INTO extracted_info (place_id, facebook, Qfb, FBLink, instagram, Qig, IGLink, meta, Qme, MetaLink, twitter, Qtw, TwitterLink, youtube, Qyt, YouTubeLink, tiktok, Qtik, TikTokLink, linkedin, Qln, LinkedInLink, phones, emails, whatsapp, Qwa, WhatsAppLink, contact, Qct, ContactLink)
        VALUES (%(place_id)s, %(facebook)s, %(Qfb)s, %(FBLink)s, %(instagram)s, %(Qig)s, %(IGLink)s, %(meta)s, %(Qme)s, %(MetaLink)s, %(twitter)s, %(Qtw)s, %(TwitterLink)s, %(youtube)s, %(Qyt)s, %(YouTubeLink)s, %(tiktok)s, %(Qtik)s, %(TikTokLink)s, %(linkedin)s, %(Qln)s, %(LinkedInLink)s, %(phones)s, %(emails)s, %(whatsapp)s, %(Qwa)s, %(WhatsAppLink)s, %(contact)s, %(Qct)s, %(ContactLink)s);
        """
        cursor.execute(insert_query, extracted_data)
        connection.commit()

        print("Datos insertados correctamente.")

    except mysql.connector.Error as err:
        print(err)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def main():
    if len(sys.argv) != 3:
        print("Uso: python urlGoogleValidator.py <place_id> <url>")
        return
    
    place_id = sys.argv[1]
    url = sys.argv[2]
    
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    print(f"Validando la URL: {url}")
    print(f"Dominio extraído: {domain}")
    
    if any(domain.endswith(known_domain) for known_domain in KNOWN_DOMAINS):
        print(f"La URL {url} es de un dominio conocido, pero procederemos con la extracción de HTML para más información.")
        html_file_path = f"/var/www/html/webpages/{place_id}.html"
        subprocess.run(['python', 'html_extractor.py', html_file_path])
    else:
        print(f"La URL {url} no es de un dominio conocido, ejecutando html_extractor.py.")
        html_file_path = f"/var/www/html/webpages/{place_id}.html"
        subprocess.run(['python', 'html_extractor.py', html_file_path])

if __name__ == "__main__":
    main()
