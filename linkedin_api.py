import requests
from requests.auth import HTTPBasicAuth
import json

# Configuración de autenticación de LinkedIn
CLIENT_ID = '77yqbhhi848az9'
CLIENT_SECRET = 'WPL_AP1.Jaq8oe9Rpi0MMYrJ.V7JnPg=='
ACCESS_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
LINKEDIN_API_URL = 'https://api.linkedin.com/v2'

def obtener_access_token():
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(ACCESS_TOKEN_URL, data=data)
    response_data = response.json()
    print(response_data)  # Imprimir los datos de respuesta para depuración
    if 'access_token' in response_data:
        return response_data['access_token']
    else:
        raise Exception('No se pudo obtener el access_token: {}'.format(response_data))

def obtener_informacion_empresa(url_perfil):
    access_token = obtener_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Extraer el ID de la empresa desde la URL del perfil
    company_id = extraer_company_id(url_perfil)
    
    # Realizar solicitud a la API de LinkedIn
    endpoint_url = f'{LINKEDIN_API_URL}/organizationalEntityAcls?q=roleAssignee&role=ADMINISTRATOR&projection=(elements*(organizationalTarget~(localizedName,vanityName,followingInfo,followerCount~(count),staffCount~(count))))&organization={company_id}'
    
    response = requests.get(endpoint_url, headers=headers)
    print(response.text)  # Imprimir la respuesta completa para depuración
    if response.status_code == 200:
        datos_empresa = response.json()
        return datos_empresa
    else:
        response.raise_for_status()

def extraer_company_id(url_perfil):
    # Extraer el ID de la empresa desde la URL del perfil de LinkedIn
    # Asumimos que la URL del perfil tiene el formato: https://www.linkedin.com/company/{company_id}/
    company_id = url_perfil.strip('/').split('/')[-1]
    return company_id

if __name__ == '__main__':
    url_perfil = input("Ingrese la URL del perfil de LinkedIn de la empresa: ")
    try:
        datos_empresa = obtener_informacion_empresa(url_perfil)
        print("Información de la empresa:")
        print(json.dumps(datos_empresa, indent=4))
    except Exception as e:
        print(f"Error al obtener información de la empresa: {e}")
