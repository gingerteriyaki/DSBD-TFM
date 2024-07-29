from flask import Flask, jsonify, request
import boto3
import pandas as pd
import os
from sklearn.externals import joblib

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
    'modelo_gbr': 'modelo_gbr.pkl'
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

@app.route('/predict', methods=['POST'])
def predict():
    client.download_file(bucket_name, file_names['modelo_gbr'], 'modelo_gbr.pkl')
    model = joblib.load('modelo_gbr.pkl')
    
    data = request.json
    data_defaults = get_defaults()
    
    for key, value in data.items():
        if value is not None:
            data_defaults[key] = value
    
    df = pd.DataFrame([data_defaults])
    prediction = model.predict(df)[0]
    
    return jsonify({'rendimiento_predicho': prediction})

def get_defaults():
    client.download_file(bucket_name, file_names['data_agricola'], 'data_agricola.xlsx')
    df_agricola = pd.read_excel('data_agricola.xlsx')
    
    client.download_file(bucket_name, file_names['datos_climaticos'], 'datos_climaticos.xlsx')
    df_climaticos = pd.read_excel('datos_climaticos.xlsx')
    
    df_agricola.columns = df_agricola.columns.str.lower()
    df_climaticos.columns = df_climaticos.columns.str.lower()
    
    df_merged = pd.merge(df_agricola, df_climaticos, on=['year', 'month', 'region'], how='inner')
    
    last_year = df_merged['year'].max()
    df_last_year = df_merged[df_merged['year'] == last_year]
    
    defaults = df_last_year.mean(numeric_only=True).to_dict()
    
    # Calcular la región más común como predeterminada
    defaults['region'] = df_last_year['region'].mode()[0]  # La región más frecuente
    
    return defaults

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
