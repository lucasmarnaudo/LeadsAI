import requests
import os

def descargar_html(place_id, url):
    try:
        print(f"Descargando HTML de {url}")
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si la respuesta tiene un error

        # Crear el directorio si no existe
        os.makedirs('/var/www/html/webpages', exist_ok=True)

        # Ruta del archivo donde se guardará el HTML
        file_path = f"/var/www/html/webpages/{place_id}.html"

        # Guardar el HTML en el archivo
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        
        print(f"HTML guardado en {file_path}")
        return file_path
    except requests.RequestException as e:
        print(f"Error al descargar HTML: {e}")
        return None
