import boto3
from botocore.client import Config
import os

def upload_to_spaces():
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='nyc3',
                            endpoint_url='https://nyc3.digitaloceanspaces.com',
                            aws_access_key_id=os.environ['SPACES_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['SPACES_SECRET_ACCESS_KEY'])

    client.upload_file('base_de_datos_clima_cleaned.csv', 'your-space-name', 'base_de_datos_clima_cleaned.csv')
    client.upload_file('consolidado_agricola_cleaned.csv', 'your-space-name', 'consolidado_agricola_cleaned.csv')
    print("Datos subidos a DigitalOcean Spaces.")

if __name__ == "__main__":
    upload_to_spaces()
