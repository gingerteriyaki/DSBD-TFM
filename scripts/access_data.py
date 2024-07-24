import boto3
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

access_key = os.getenv('SPACES_ACCESS_KEY_ID')
secret_key = os.getenv('SPACES_SECRET_ACCESS_KEY')

# Configurar cliente de boto3 para DigitalOcean Spaces
session = boto3.session.Session()
client = session.client('s3',
                        region_name='fra1',
                        endpoint_url='https://climaplatano.fra1.digitaloceanspaces.com',
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key)

# Función para descargar archivos de DigitalOcean Spaces
def download_file(bucket_name, object_name, file_name):
    client.download_file(bucket_name, object_name, file_name)
    print(f"{object_name} descargado como {file_name}")

# Lista de archivos a descargar
files_to_download = [
    {'object_name': 'climaplatano/datos_agricola_consolidados.xlsx', 'file_name': 'datos_agricola_consolidados.xlsx'},
    {'object_name': 'climaplatano/datos_climaticos.xlsx', 'file_name': 'datos_climaticos.xlsx'},
    {'object_name': 'climaplatano/datos_cosecha_mensuales.xlsx', 'file_name': 'datos_cosecha_mensuales.xlsx'},
    {'object_name': 'climaplatano/datos_produccion_mensuales.xlsx', 'file_name': 'datos_produccion_mensuales.xlsx'},
    {'object_name': 'climaplatano/datos_siembra_mensuales.xlsx', 'file_name': 'datos_siembra_mensuales.xlsx'}
]

bucket_name = 'climaplatano'

# Descargar cada archivo
for file in files_to_download:
    download_file(bucket_name, file['object_name'], file['file_name'])