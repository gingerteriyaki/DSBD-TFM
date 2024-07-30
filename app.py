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
    
@app.route('/predict', methods=['GET'])
def predict_rendimiento():
    # Descargar y cargar el modelo desde DigitalOcean Spaces
    client.download_file(bucket_name, file_names['modelo_gbr'], 'modelo_gbr.pkl')
    model = joblib.load('modelo_gbr.pkl')

    # Obtener los parámetros de la solicitud
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=str)
    region = request.args.get('region', type=str)
    siembra_mensual = request.args.get('siembra_mensual', type=float)
    cosecha_mensual = request.args.get('cosecha_mensual', type=float)
    produccion_mensual = request.args.get('produccion_mensual', type=float)
    precipitation = request.args.get('precipitation', type=float)
    max_temp = request.args.get('max_temp', type=float)
    min_temp = request.args.get('min_temp', type=float)
    humidity = request.args.get('humidity', type=float)

    # Calcular características adicionales
    temp_diff = max_temp - min_temp
    precip_per_humidity = precipitation / humidity
    siembra_vs_cosecha = siembra_mensual / cosecha_mensual
    produccion_vs_siembra = produccion_mensual / siembra_mensual

    # Crear DataFrame con los valores proporcionados
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
    resultado = {
        'year': year,
        'month': month,
        'region': region,
        'siembra_mensual': siembra_mensual,
        'cosecha_mensual': cosecha_mensual,
        'produccion_mensual': produccion_mensual,
        'precipitation': precipitation,
        'max_temp': max_temp,
        'min_temp': min_temp,
        'humidity': humidity,
        'prediccion_rendimiento': prediccion[0]
    }

    return render_template('resultado.html', resultado=resultado)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
