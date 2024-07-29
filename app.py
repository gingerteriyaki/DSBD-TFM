from flask import Flask, jsonify
import boto3
import pandas as pd
import os

app = Flask(__name__)

# Configurar el cliente de S3
session = boto3.session.Session()
client = session.client('s3',
                        region_name='fra1',
                        endpoint_url='https://climaplatano.fra1.digitaloceanspaces.com',
                        aws_access_key_id=os.environ['SPACES_ACCESS_KEY_ID'],
                        aws_secret_access_key=os.environ['SPACES_SECRET_ACCESS_KEY'])

bucket_name = 'climaplatano'
file_names = {
    'data_agricola': 'data_agricola.xlsx',
    'datos_climaticos': 'datos_climaticos.xlsx',
    # Agrega más archivos según sea necesario
}

@app.route('/data_agricola', methods=['GET'])
def obtener_datos_mensuales():
    # Descargar el archivo desde DigitalOcean Spaces
    client.download_file(bucket_name, file_names['data_agricola'], 'data_agricola.xlsx')
    
    # Leer el archivo Excel
    df = pd.read_excel('data_agricola.xlsx')
    
    # Convertir a JSON
    datos_json = df.to_json(orient='records')
    
    return jsonify(datos_json)

@app.route('/datos_climaticos', methods=['GET'])
def obtener_datos_climaticos():
    # Descargar el archivo desde DigitalOcean Spaces
    client.download_file(bucket_name, file_names['datos_climaticos'], 'datos_climaticos.xlsx')
    
    # Leer el archivo Excel
    df = pd.read_excel('datos_climaticos.xlsx')
    
    # Convertir a JSON
    datos_json = df.to_json(orient='records')
    
    return jsonify(datos_json)

# Agrega más rutas para otros archivos si es necesario

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
