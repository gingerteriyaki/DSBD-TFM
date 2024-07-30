from flask import Flask, request, jsonify, render_template
import boto3
import pandas as pd
import os
import joblib
import numpy as np
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

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

@app.route('/')
def home():
    current_year = datetime.now().year
    return render_template('formulario.html', current_year=current_year)

@app.route('/data_agricola', methods=['GET'])
def obtener_datos_mensuales():
    client.download_file(bucket_name, file_names['data_agricola'], 'data_agricola.xlsx')
    df = pd.read_excel('data_agricola.xlsx')
    datos_json = df.to_json(orient='records')
    return jsonify(datos_json)

@app.route('/datos_climaticos', methods=['GET'])
def obtener_datos_climaticos():
    client.download_file(bucket_name, file_names['datos_climaticos'], 'datos_climaticos.xlsx')
    df = pd.read_excel('datos_climaticos.xlsx')
    datos_json = df.to_json(orient='records')
    return jsonify(datos_json)

@app.route('/predict', methods=['GET'])
def predict_rendimiento():
    client.download_file(bucket_name, file_names['modelo_gbr'], 'modelo_gbr.pkl')
    model = joblib.load('modelo_gbr.pkl')

    client.download_file(bucket_name, file_names['datos_climaticos'], 'datos_climaticos.xlsx')
    client.download_file(bucket_name, file_names['data_agricola'], 'data_agricola.xlsx')

    datos_climaticos = pd.read_excel('datos_climaticos.xlsx')
    datos_agricola = pd.read_excel('data_agricola.xlsx')

    datos_climaticos.columns = datos_climaticos.columns.str.lower()
    datos_agricola.columns = datos_agricola.columns.str.lower()

    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    region = request.args.get('region', type=str)
    siembra_mensual = request.args.get('siembra_mensual', type=float)
    cosecha_mensual = request.args.get('cosecha_mensual', type=float)
    produccion_mensual = request.args.get('produccion_mensual', type=float)
    precipitation = request.args.get('precipitation', default=None, type=float)
    max_temp = request.args.get('max_temp', default=None, type=float)
    min_temp = request.args.get('min_temp', default=None, type=float)
    humidity = request.args.get('humidity', default=None, type=float)

    temp_diff = max_temp - min_temp if max_temp is not None and min_temp is not None else None
    precip_per_humidity = precipitation / humidity if precipitation is not None and humidity is not None else None
    siembra_vs_cosecha = siembra_mensual / cosecha_mensual if siembra_mensual is not None and cosecha_mensual is not None else None
    produccion_vs_siembra = produccion_mensual / siembra_mensual if produccion_mensual is not None and siembra_mensual is not None else None

    data = pd.DataFrame({
        'year': [year],
        'month': [month],
        'region': [region],
        'siembra_mensual': [siembra_mensual],
        'cosecha_mensual': [cosecha_mensual],
        'produccion_mensual': [produccion_mensual],
        'precipitation': [precipitation],
        'max_temp': [max_temp],
        'min_temp': [min_temp],
        'humidity': [humidity],
        'temp_diff': [temp_diff],
        'precip_per_humidity': [precip_per_humidity],
        'siembra_vs_cosecha': [siembra_vs_cosecha],
        'produccion_vs_siembra': [produccion_vs_siembra]
    })

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
