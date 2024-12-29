# social_api_helper.py

import requests

def get_facebook_followers(url):
    api_url = f"https://social-network-brand-api.keepcon.com/facebook?url={url}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        followers_count = data.get('followers_count', 0)
        return followers_count
    except requests.RequestException as e:
        print(f"Error al obtener seguidores de Facebook: {e}")
        return 0

def get_instagram_followers(url):
    api_url = f"https://social-network-brand-api.keepcon.com/instagram?url={url}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        followers_count = data.get('followers_count', 0)
        return followers_count
    except requests.RequestException as e:
        print(f"Error al obtener seguidores de Instagram: {e}")
        return 0

def get_twitter_followers(url):
    api_url = f"https://social-network-brand-api.keepcon.com/twitter?url={url}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        followers_count = data.get('followers_count', 0)
        return followers_count
    except requests.RequestException as e:
        print(f"Error al obtener seguidores de Twitter: {e}")
        return 0

def get_youtube_subscribers(url):
    api_url = f"https://social-network-brand-api.keepcon.com/youtube?url={url}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        subscribers_count = data.get('subscribers_count', 0)
        return subscribers_count
    except requests.RequestException as e:
        print(f"Error al obtener suscriptores de YouTube: {e}")
        return 0

def get_tiktok_followers(url):
    api_url = f"https://social-network-brand-api.keepcon.com/tiktok?url={url}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        followers_count = data.get('followers_count', 0)
        return followers_count
    except requests.RequestException as e:
        print(f"Error al obtener seguidores de TikTok: {e}")
        return 0

def get_linkedin_followers(url):
    api_url = f"https://social-network-brand-api.keepcon.com/linkedin?url={url}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        followers_count = data.get('followers_count', 0)
        return followers_count
    except requests.RequestException as e:
        print(f"Error al obtener seguidores de LinkedIn: {e}")
        return 0

# Agrega más funciones para otras redes sociales si es necesario.
