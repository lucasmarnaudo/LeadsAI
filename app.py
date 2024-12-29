import logging
import os
import json
import db_config
import time
import mysql.connector
import requests
from flask import Flask, request, render_template, jsonify
from subprocess import run, CalledProcessError
from url_checker import validar_url
from response_formatter import format_response
from google_helper import search_places, get_place_details
from openai_helper import detectar_problemas
import html_extractor

app = Flask(__name__)

# Configuración de Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Formateador
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Manejador de archivo
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Manejador de consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Evitar propagación
logger.propagate = False

def load_api_keys():
    keys = {}
    try:
        with open('keys.data', 'r') as file:
            for line in file:
                key, value = line.strip().split(' = ')
                keys[key.strip()] = value.strip('\'')
        logger.info("Claves API cargadas exitosamente.")
    except Exception as e:
        logger.exception(f"Error al cargar las claves API: {e}")
    return keys

keys = load_api_keys()
openai_api_key = keys.get('openai.api_key')
google_maps_api_key = keys.get('google_maps_api_key')

@app.route('/')
def index():
    logger.info("Acceso a la ruta principal.")
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar():
    logger.info("Iniciando ruta /buscar")
    start_time = time.time()

    try:
        if request.is_json:
            logger.debug("Solicitud recibida en formato JSON")
            data = request.get_json()
            palabras = data.get('palabras', '').split('\n')
            pais = data.get('pais', '')
            tipo_busqueda = data.get('tipo_busqueda', 'Full')
            response_type = 'json'
        else:
            logger.debug("Solicitud recibida en formato form-data")
            palabras = request.form.get('palabras', '').split('\n')
            pais = request.form.get('pais', '')
            tipo_busqueda = request.form.get('tipo_busqueda', 'Full')
            response_type = 'web'

        logger.info(f"Palabras a buscar: {palabras}")
        logger.info(f"País seleccionado: {pais}")
        logger.info(f"Tipo de búsqueda: {tipo_busqueda}")

        resultados = []
        json_data_list = []

        for palabra in palabras:
            query = f"{palabra.strip()} {pais}".strip()
            logger.debug(f"Procesando palabra: {query}")

            # Llamada a la función search_places en google_helper.py
            places = search_places(query, google_maps_api_key, logger)
            if not places:
                logger.error("No se encontraron lugares.")
                continue

            connection, cursor = db_config.connect()
            if not connection or not cursor:
                logger.error("No se pudo conectar a la base de datos.")
                continue

            for place in places:
                place_id = place.get('place_id')

                # Llamada a la función get_place_details en google_helper.py
                details_data = get_place_details(place_id, google_maps_api_key, logger)
                if not details_data:
                    logger.error(f"No se pudieron obtener detalles para el place_id: {place_id}")
                    continue

                name = details_data.get('name')
                address = details_data.get('formatted_address')
                types = details_data.get('types', [])
                google_maps_uri = details_data.get('url', 'No URL found')
                website = details_data.get('website', 'No website found')
                reviews = details_data.get('reviews', [])
                rating = details_data.get('rating', 0)
                html_file_path = f"/var/www/html/places/{place_id}.html"

                # Insertar o actualizar en la tabla places_details
                try:
                    # Crear la tabla si no existe
                    create_table_query = """
                    CREATE TABLE IF NOT EXISTS places_details (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        place_id VARCHAR(255) NOT NULL UNIQUE,
                        name VARCHAR(255) NOT NULL,
                        address VARCHAR(255),
                        types JSON,
                        rating FLOAT,
                        reviews TEXT,
                        query_text VARCHAR(255) NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        google_maps_uri VARCHAR(255),
                        website VARCHAR(255),
                        formatted_address VARCHAR(255),
                        json_file_path VARCHAR(255),
                        checkedURL VARCHAR(255),
                        html_file_path VARCHAR(255),
                        tipo_busqueda VARCHAR(255)
                    );
                    """
                    cursor.execute(create_table_query)

                    # Insertar o actualizar los datos
                    insert_details_query = """
                    INSERT INTO places_details (place_id, name, address, types, rating, reviews, query_text, google_maps_uri, website, formatted_address, html_file_path, tipo_busqueda)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        name = VALUES(name),
                        address = VALUES(address),
                        types = VALUES(types),
                        rating = VALUES(rating),
                        reviews = VALUES(reviews),
                        query_text = VALUES(query_text),
                        google_maps_uri = VALUES(google_maps_uri),
                        website = VALUES(website),
                        formatted_address = VALUES(formatted_address),
                        html_file_path = VALUES(html_file_path),
                        tipo_busqueda = VALUES(tipo_busqueda);
                    """
                    cursor.execute(insert_details_query, (
                        place_id,
                        name,
                        address,
                        json.dumps(types),
                        rating,
                        json.dumps(reviews),
                        query,
                        google_maps_uri,
                        website,
                        address,
                        html_file_path,
                        tipo_busqueda
                    ))
                    connection.commit()
                    logger.info(f"Datos insertados/actualizados en places_details para place_id: {place_id}")
                except mysql.connector.Error as err:
                    logger.error(f"Error al insertar/actualizar en places_details: {err}")

                # Descargar y guardar el contenido HTML de la página web
                if website != 'No website found':
                    try:
                        logger.debug(f"Descargando contenido HTML de: {website}")
                        html_content = requests.get(website, timeout=10)
                        html_content.raise_for_status()
                        with open(html_file_path, 'w', encoding='utf-8') as file:
                            file.write(html_content.text)
                        logger.info(f"Archivo HTML guardado en {html_file_path}")
                    except requests.RequestException as e:
                        logger.error(f"Error al descargar el HTML de {website}: {e}")
                        continue  # Saltar al siguiente lugar

                # Validar URL
                try:
                    logger.debug(f"Ejecutando urlGoogleValidator.py para place_id: {place_id} y checked_url: {website}")
                    run(['python', 'urlGoogleValidator.py', place_id, website], check=True)
                    logger.debug(f"urlGoogleValidator.py ejecutado exitosamente para place_id: {place_id}")
                except CalledProcessError as e:
                    logger.error(f"Error al ejecutar urlGoogleValidator.py: {e}")

                # Extraer comentarios y detectar problemas
                comentarios = "\n".join([review.get('text', '') for review in reviews])

                problemas = []
                if tipo_busqueda == 'Full' and comentarios:
                    logger.debug("Detectando problemas mediante OpenAI")
                    problemas = detectar_problemas(comentarios, openai_api_key, logger)
                    logger.debug(f"Problemas detectados: {problemas}")

                # Obtener datos extraídos
                json_data_str = html_extractor.extract_info(html_file_path, db_config)

                if json_data_str is None:
                    logger.error(f"html_extractor.extract_info devolvió None para {html_file_path}")
                    json_data = {}
                    # Actualizar la base de datos indicando el error
                    try:
                        cursor.execute("""
                            UPDATE extracted_info
                            SET problems = %s
                            WHERE place_id = %s
                        """, (json.dumps(["error al extraer información"]), place_id))
                        connection.commit()
                        logger.info(f"Actualizado 'problems' con 'error al extraer información' para place_id: {place_id}")
                    except mysql.connector.Error as err:
                        logger.error(f"Error al actualizar la base de datos con el error: {err}")
                else:
                    try:
                        json_data = json.loads(json_data_str)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error al parsear JSON de html_extractor: {e}")
                        json_data = {}
                        # Actualizar la base de datos indicando el error
                        try:
                            cursor.execute("""
                                UPDATE extracted_info
                                SET problems = %s
                                WHERE place_id = %s
                            """, (json.dumps(["error al parsear JSON"]), place_id))
                            connection.commit()
                            logger.info(f"Actualizado 'problems' con 'error al parsear JSON' para place_id: {place_id}")
                        except mysql.connector.Error as err:
                            logger.error(f"Error al actualizar la base de datos con el error: {err}")

                # Añadir problemas al JSON
                if problemas:
                    json_data['problems'] = problemas
                    try:
                        cursor.execute("""
                            UPDATE extracted_info
                            SET problems = %s
                            WHERE place_id = %s
                        """, (json.dumps(problemas), place_id))
                        connection.commit()
                        logger.info(f"Problemas guardados en la base de datos para place_id: {place_id}")
                    except mysql.connector.Error as err:
                        logger.error(f"Error al guardar problemas en la base de datos: {err}")

                json_data_list.append(json_data)
                resultados.append(json_data)

            cursor.close()
            connection.close()
            logger.debug("Conexión a la base de datos cerrada.")

        end_time = time.time()
        tiempo_respuesta = end_time - start_time
        logger.info(f"Tiempo de respuesta: {tiempo_respuesta} segundos")

        # Usar el JSON más reciente generado
        final_json_data = json_data_list[-1] if json_data_list else {}
        logger.debug(f"JSON final generado en app.py: {final_json_data}")

        if response_type == 'json':
            logger.debug("Devolviendo respuesta en formato JSON.")
            return format_response(final_json_data, response_type)
        else:
            logger.debug("Devolviendo respuesta en formato web.")
            return format_response(final_json_data, response_type)

    except Exception as e:
        logger.exception(f"Excepción general en la ruta /buscar: {e}")
        return jsonify({"error": "Ocurrió un error procesando la solicitud"}), 500

if __name__ == '__main__':
    logger.info("Iniciando la aplicación Flask.")
    app.run(host='0.0.0.0', port=5000, debug=True)
