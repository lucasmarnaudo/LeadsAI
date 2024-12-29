import requests

def search_places(query, api_key, logger=None):
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": api_key
    }
    try:
        if logger:
            logger.debug(f"Realizando solicitud a Google Maps API: {search_url} con params: {params}")
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        places = data.get('results', [])
        if logger:
            logger.debug(f"Places obtenidos: {len(places)}")
        return places
    except requests.RequestException as e:
        if logger:
            logger.error(f"Error en la solicitud a Google Maps API: {e}")
        return []

def get_place_details(place_id, api_key, logger=None):
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,types,rating,website,reviews,url",
        "key": api_key
    }
    try:
        if logger:
            logger.debug(f"Solicitando detalles del lugar: {details_url} con params: {params}")
        response = requests.get(details_url, params=params)
        response.raise_for_status()
        data = response.json()
        result = data.get('result', {})
        return result
    except requests.RequestException as e:
        if logger:
            logger.error(f"Error en la solicitud de detalles: {e}")
        return {}