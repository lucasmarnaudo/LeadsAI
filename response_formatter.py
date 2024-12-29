import json
from flask import jsonify

# Función para formatear la respuesta basada en los datos JSON proporcionados
def format_response(datos, response_type='web'):
    print("Datos recibidos en format_response:", datos)  # Log

    if response_type == 'web':
        return jsonify({
            'origen': 'web',
            'datos': datos
        })
    elif response_type == 'json':
        return jsonify({
            'origen': 'CURL',
            'datos': datos
        })
    else:
        return jsonify({
            'origen': 'desconocido',
            'datos': datos
        })

if __name__ == "__main__":
    # Ejemplo de uso:
    example_datos = {
        "place_id": "ChIJ76c24t2YMpQRKEI4dKZhJ5Q",
        "facebook": True,
        "Qfb": 1,
        "FBLink": ["https://www.facebook.com/WiseCX"],
        "instagram": True,
        "Qig": 1,
        "IGLink": ["https://www.instagram.com/wise_cx/"],
        "meta": False,
        "Qme": 0,
        "MetaLink": [],
        "twitter": False,
        "Qtw": 0,
        "TwitterLink": [],
        "youtube": True,
        "Qyt": 1,
        "YouTubeLink": ["https://www.youtube.com/channel/UC7eVMuXwrJ6PB2BBsSyLB_Q"],
        "tiktok": False,
        "Qtik": 0,
        "TikTokLink": [],
        "linkedin": True,
        "Qln": 1,
        "LinkedInLink": ["https://www.linkedin.com/company/wise-cx/"],
        "whatsapp": False,
        "Qwa": 0,
        "WhatsAppLink": [],
        "contact": True,
        "Qct": 3,
        "ContactLink": ["https://wisecx.com/contacto/", "https://wisecx.com/contacto/", "https://wisecx.com/contacto/"],
        "phones": [],
        "emails": []
    }
    print(format_response(example_datos, 'web'))
