from flask import Flask, request, jsonify
import boto3
import pandas as pd
import os
import joblib
import numpy as np

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

@app.route('/predict', methods=['GET'])
def predict_rendimiento():
    # Descargar y cargar el modelo desde DigitalOcean Spaces
    client.download_file(bucket_name, file_names['modelo_gbr'], 'modelo_gbr.pkl')
    model = joblib.load('modelo_gbr.pkl')

    # Descargar datos para obtener valores por defecto
    client.download_file(bucket_name, file_names['datos_climaticos'], 'datos_climaticos.xlsx')
    client.download_file(bucket_name, file_names['data_agricola'], 'data_agricola.xlsx')

    datos_climaticos = pd.read_excel('datos_climaticos.xlsx')
    datos_agricola = pd.read_excel('data_agricola.xlsx')

    # Convertir las columnas a minúsculas para asegurar la consistencia
    datos_climaticos.columns = datos_climaticos.columns.str.lower()
    datos_agricola.columns = datos_agricola.columns.str.lower()

    # Verificar nombres de las columnas
    print(f"Datos climáticos columnas: {datos_climaticos.columns}")
    print(f"Datos agrícolas columnas: {datos_agricola.columns}")

    # Obtener el último año disponible en los datos
    ultimo_año = datos_climaticos['year'].max()

    # Obtener los parámetros de la solicitud, usando valores predeterminados cuando sea necesario
    year = request.args.get('year', default=ultimo_año, type=int)
    month = request.args.get('month', default=int(datos_climaticos['month'].mode()[0]), type=int)
    region = request.args.get('region', default=datos_climaticos['region'].mode()[0], type=str)
    siembra_mensual = request.args.get('siembra_mensual', default=None, type=float)
    cosecha_mensual = request.args.get('cosecha_mensual', default=None, type=float)
    precipitation = request.args.get('precipitation', default=None, type=float)
    max_temp = request.args.get('max_temp', default=None, type=float)
    min_temp = request.args.get('min_temp', default=None, type=float)
    humidity = request.args.get('humidity', default=None, type=float)

    # Obtener valores por defecto si no se proporcionaron
    defaults = get_defaults(datos_agricola, datos_climaticos, ultimo_año, month, region)
    siembra_mensual = siembra_mensual if siembra_mensual is not None else defaults['siembra_mensual']
    cosecha_mensual = cosecha_mensual if cosecha_mensual is not None else defaults['cosecha_mensual']
    precipitation = precipitation if precipitation is not None else defaults['precipitation']
    max_temp = max_temp if max_temp is not None else defaults['max_temp']
    min_temp = min_temp if min_temp is not None else defaults['min_temp']
    humidity = humidity if humidity is not None else defaults['humidity']

    # Calcular características adicionales
    temp_diff = max_temp - min_temp
    precip_per_humidity = precipitation / humidity
    siembra_vs_cosecha = siembra_mensual / cosecha_mensual
    produccion_vs_siembra = defaults['produccion_mensual'] / siembra_mensual

    # Crear DataFrame con los valores proporcionados o por defecto
    data = pd.DataFrame({
        'year': [year],
        'month': [month],
        'region': [region],
        'siembra_mensual': [siembra_mensual],
        'cosecha_mensual': [cosecha_mensual],
        'precipitation': [precipitation],
        'max_temp': [max_temp],
        'min_temp': [min_temp],
        'humidity': [humidity],
        'temp_diff': [temp_diff],
        'precip_per_humidity': [precip_per_humidity],
        'siembra_vs_cosecha': [siembra_vs_cosecha],
        'produccion_vs_siembra': [produccion_vs_siembra]
    })

    # Hacer predicción
    prediccion = model.predict(data)
    resultado = {'prediccion_rendimiento': prediccion[0]}

    return jsonify(resultado)

def get_defaults(datos_agricola, datos_climaticos, year, month, region):
    promedio_agricola = datos_agricola[(datos_agricola['year'] == year) & (datos_agricola['month'] == month) & (datos_agricola['region'] == region)].mean(numeric_only=True)
    promedio_climatico = datos_climaticos[(datos_climaticos['year'] == year) & (datos_climaticos['month'] == month) & (datos_climaticos['region'] == region)].mean(numeric_only=True)

    defaults = {
        'siembra_mensual': promedio_agricola['siembra_mensual'],
        'cosecha_mensual': promedio_agricola['cosecha_mensual'],
        'produccion_mensual': promedio_agricola['produccion_mensual'],
        'precipitation': promedio_climatico['precipitation'],
        'max_temp': promedio_climatico['max_temp'],
        'min_temp': promedio_climatico['min_temp'],
        'humidity': promedio_climatico['humidity']
    }
    return defaults

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)