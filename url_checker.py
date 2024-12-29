import requests
import logging
import time

# Configurar el archivo de log
logging.basicConfig(filename='process.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def validar_url(url, attempt=1):
    original_url = url
    final_url = url

    try:
        config = {
            'timeout': 10,
            'headers': {},
            'verify': True  # Verificación de certificados SSL/TLS por defecto
        }

        # Estrategias de reintento
        if attempt == 2:
            url = url.replace('https://', 'http://')
        elif attempt == 3:
            config['headers']['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        elif attempt == 4:
            url = url + 'home/' if url.endswith('/') else url + '/home/'
        elif attempt == 5:
            config['verify'] = False  # No verificar el certificado SSL/TLS
        elif attempt == 6:
            url = url.replace('www.', '')

        response = requests.get(url, **config)
        logging.info(f'{url}: {response.status_code}')
        final_url = url  # URL accesible
    except requests.RequestException as error:
        if attempt >= 6:
            error_message = f'URL final con "." debido a múltiples fallos en la validación: {str(error)}'
            logging.error(f'{url}: {error_message} (Final attempt)')
            final_url = original_url + '.'
        else:
            logging.warning(f'{url}: Error en la validación (Intento {attempt}/6) - Reintentando...')
            time.sleep(1)  # Esperar un segundo antes de reintentar
            return validar_url(url, attempt + 1)

    return final_url

# Prueba de función
if __name__ == '__main__':
    # Ejemplo de uso
    test_url = "https://www.example.com"
    checked_url = validar_url(test_url)
    print(f'Checked URL: {checked_url}')
