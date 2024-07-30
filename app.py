from flask import Flask, render_template, request, jsonify
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
model_filename = 'modelo_gbr.pkl'

# Descargar y cargar el modelo desde DigitalOcean Spaces
try:
    if not os.path.exists('model'):
        os.makedirs('model')
    client.download_file(bucket_name, model_filename, f'model/{model_filename}')
    model = joblib.load(f'model/{model_filename}')
except Exception as e:
    print(f"Error al descargar o cargar el modelo: {e}")
    raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Obtener datos del formulario
        data = request.get_json()
        print("Datos recibidos:", data)

        # Definir los campos necesarios y opcionales
        essential_fields = ['nombre', 'apellido', 'year', 'month', 'region', 'siembra_mensual', 'cosecha_mensual', 'produccion_mensual']
        optional_fields = ['precipitation', 'max_temp', 'min_temp', 'humidity']

        # Verificar que los campos esenciales están presentes
        for field in essential_fields:
            if field not in data:
                print(f"Falta campo esencial: {field}")
                return jsonify({'error': f"Falta campo esencial: {field}"}), 400

        # Convertir a DataFrame y asegurar tipos de datos
        df = pd.DataFrame([data])
        df = df.astype({
            'year': int,
            'month': int,
            'siembra_mensual': float,
            'cosecha_mensual': float,
            'produccion_mensual': float
        })

        # Datos climáticos históricos promedio por mes (se puede ajustar para ser dinámico)
        historical_climate_data = {
            'precipitation': [59.233, 65.910, 76.814, 110.040, 225.277, 104.683, 143.423, 153.988, 158.602, 166.055, 166.373, 93.170],
            'max_temp': [28.590, 28.997, 29.728, 30.431, 30.651, 31.769, 31.757, 32.065, 32.026, 31.399, 30.024, 28.710],
            'min_temp': [17.250, 17.565, 17.869, 18.719, 19.693, 20.623, 20.664, 20.988, 20.537, 20.123, 19.367, 18.088],
            'humidity': [79.632, 78.329, 76.857, 78.117, 80.691, 79.896, 79.126, 79.851, 81.525, 82.935, 82.974, 81.047]
        }

        # Estimar datos opcionales si no se proporcionan
        month_index = int(data['month']) - 1  # Índice del mes para acceder a los promedios
        for field in optional_fields:
            if field not in data or data[field] == '':
                df[field] = historical_climate_data[field][month_index]
            else:
                df[field] = float(data[field])

        # Calcular características derivadas si son necesarias
        df['temp_diff'] = df['max_temp'] - df['min_temp']
        df['precip_per_humidity'] = df['precipitation'] / df['humidity']
        df['siembra_vs_cosecha'] = df['siembra_mensual'] / df['cosecha_mensual']
        df['produccion_vs_siembra'] = df['produccion_mensual'] / df['siembra_mensual']

        # Realizar la predicción
        prediccion = model.predict(df)

        # Respuesta con el resultado
        return jsonify({'rendimiento_predicho': prediccion[0]})
    except Exception as e:
        # Manejo de errores
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
