import openai
import logging

# Configuración de Logging (opcional, si deseas logging específico en este módulo)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def detectar_problemas(comentarios, api_key, logger=None):
    openai.api_key = api_key
    prompt = (
        "Analiza los siguientes comentarios de clientes y extrae los problemas principales "
        "identificados en forma de frases de 3 o 4 palabras, ordenadas por el impacto que "
        "pueden tener en la imagen de la empresa:\n\n" + comentarios
    )
    try:
        if logger:
            logger.debug("Enviando solicitud a OpenAI API para detectar problemas.")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        problemas = response.choices[0].message['content'].strip()
        problemas_lista = [problema.strip('- ').strip() for problema in problemas.split('\n') if problema.strip()]
        if logger:
            logger.debug(f"Problemas detectados: {problemas_lista}")
        return problemas_lista
    except Exception as e:
        if logger:
            logger.error(f"Error al detectar problemas con OpenAI: {e}")
        return []