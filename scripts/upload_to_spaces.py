import boto3
from botocore.client import Config
import os

def upload_to_spaces():
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='fra1',
                            endpoint_url='https://climaplatano.fra1.digitaloceanspaces.com',
                            aws_access_key_id=os.environ['SPACES_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['SPACES_SECRET_ACCESS_KEY'])

    space_name = 'climaplatano'  # Asegúrate de que esto sea correcto

    # Lista de archivos a subir
    files_to_upload = [
        'consolidado_agricola_general.xlsx',
        'datos_climaticos.xlsx',
        'datos_siembra_mensuales.xlsx',
        'datos_produccion_mensuales.xlsx',
        'datos_cosecha_mensuales.xlsx',
        'data_agricola.xlsx',
        'modelo_gbr.pkl'
    ]

    for file_name in files_to_upload:
        client.upload_file(file_name, space_name, file_name)
        print(f"{file_name} subido a DigitalOcean Spaces.")

if __name__ == "__main__":
    upload_to_spaces()
