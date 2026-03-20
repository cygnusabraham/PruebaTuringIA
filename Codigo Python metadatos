# Importa la librería necesaria para manejar eventos de Google Cloud (CloudEvents)
import functions_framework

# Importa la librería estándar de Python para generar registros (logs)
import logging

# Configura el sistema de logs para que muestre mensajes de nivel INFO en adelante
logging.basicConfig(level=logging.INFO)

# Crea una instancia del logger con el nombre del archivo actual para identificar el origen de los mensajes
logger = logging.getLogger(__name__)

# Decorador que indica que esta función responderá a un evento de tipo CloudEvent (enviado por Eventarc)
@functions_framework.cloud_event
def extraer_metadatos(cloud_event):
    
    # Extrae el diccionario 'data' del evento recibido, que contiene la información del objeto de Storage
    data = cloud_event.data
    
    # Obtiene el nombre del archivo subido (ej: "foto.png") del diccionario de datos
    nombre = data.get("name")
    
    # Obtiene el nombre del bucket de origen (donde se subió el archivo)
    bucket = data.get("bucket")
    
    # Obtiene el peso del archivo en bytes
    tamanio = data.get("size")
    
    # Obtiene el formato del archivo (ej: "image/png" o "text/plain")
    tipo = data.get("contentType")

    # Envía un mensaje informativo a Cloud Logging indicando que la detección fue exitosa
    logger.info("--- ¡ARCHIVO DETECTADO CON ÉXITO! ---")
    
    # Registra en los logs el nombre específico del archivo detectado
    logger.info(f"Nombre: {nombre}")
    
    # Registra en los logs el nombre del bucket procesado
    logger.info(f"Bucket: {bucket}")
    
    # Registra el tamaño del archivo para control y auditoría
    logger.info(f"Tamaño: {tamanio} bytes")
    
    # Registra el tipo de contenido para saber qué tipo de archivo se está manejando
    logger.info(f"Tipo: {tipo}")
