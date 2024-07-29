import os
import boto3
from dotenv import load_dotenv

def download_files():
    # Cargar variables de entorno desde el archivo .env
    load_dotenv()

    # Configurar cliente de DigitalOcean Spaces
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='fra1',
                            endpoint_url='https://climaplatano.fra1.digitaloceanspaces.com',
                            aws_access_key_id=os.environ['SPACES_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['SPACES_SECRET_ACCESS_KEY'])

    # Función para descargar un archivo desde DigitalOcean Spaces
    def download_file_from_space(bucket_name, object_name, file_name):
        client.download_file(bucket_name, object_name, file_name)
        print(f"{file_name} descargado con éxito.")

    # Nombres de los archivos en el bucket y local
    files_to_download = {
        'datos_climaticos.xlsx': 'datos_climaticos.xlsx',
        'datos_mensuales_por_region.xlsx': 'datos_mensuales_por_region.xlsx'
    }


    bucket_name = 'climaplatano'

    # Descargar los archivos
    for object_name, file_name in files_to_download.items():
        download_file_from_space(bucket_name, object_name, file_name)

if __name__ == "__main__":
    download_files()
