import boto3
from botocore.client import Config
import os

def upload_to_spaces():
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='fra1',
                            endpoint_url='https://climaplatano.fra1.digitaloceanspaces.com',
                            aws_access_key_id=os.environ['DO00DAZTRTXVBN4KUZMU'],
                            aws_secret_access_key=os.environ['wC98p12ouNcoFDJTWcf7RrVc0GOFZaZT6pUSZ7LggQo'])

    space_name = 'climaplatano'  # Asegúrate de que esto sea correcto

    # Lista de archivos a subir
    files_to_upload = [
        'datos_agricola_consolidados_mod.xlsx',
        'datos_climaticos.xlsx',
        'datos_siembra_mensuales.xlsx',
        'datos_produccion_mensuales.xlsx',
        'datos_cosecha_mensuales_mod.xlsx',
        'datos_mensuales_por_region.xlsx'
    ]

    for file_name in files_to_upload:
        client.upload_file(file_name, space_name, file_name)
        print(f"{file_name} subido a DigitalOcean Spaces.")

if __name__ == "__main__":
    upload_to_spaces()
