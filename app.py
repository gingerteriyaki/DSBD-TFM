from flask import Flask, request, jsonify, render_template
import boto3
import pandas as pd
import os
import joblib

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

@app.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        # Procesar los datos del formulario y redirigir a /predict
        return render_template('formulario.html')

    # Si es GET, simplemente renderiza el formulario
    return render_template('formulario.html')

@app.route('/predict', methods=['POST'])
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

    # Obtener el último año disponible en los datos
    ultimo_año = datos_climaticos['year'].max()

    # Obtener los parámetros del formulario
    year = int(request.form['year'])
    month = int(request.form['month'])
    region = request.form['region']
    siembra_mensual = float(request.form['siembra_mensual'])
    cosecha_mensual = float(request.form['cosecha_mensual'])
    precipitation = float(request.form.get('precipitation', 0))  # Default to 0 if not provided
    max_temp = float(request.form.get('max_temp', 0))  # Default to 0 if not provided
    min_temp = float(request.form.get('min_temp', 0))  # Default to 0 if not provided
    humidity = float(request.form.get('humidity', 0))  # Default to 0 if not provided

    # Calcular características adicionales
    temp_diff = max_temp - min_temp
    precip_per_humidity = precipitation / humidity if humidity != 0 else 0  # Avoid division by zero
    siembra_vs_cosecha = siembra_mensual / cosecha_mensual if cosecha_mensual != 0 else 0  # Avoid division by zero
    produccion_vs_siembra = datos_agricola[(datos_agricola['year'] == year) &
                                           (datos_agricola['month'] == month) &
                                           (datos_agricola['region'] == region)]['produccion_mensual'].values[0] / siembra_mensual if siembra_mensual != 0 else 0  # Avoid division by zero

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
    resultado = {'prediccion_rendimiento': prediccion[0]}

    # Calcular rendimiento de cultivo actual (ejemplo)
    rendimiento_actual = siembra_mensual - cosecha_mensual

    # Renderizar la plantilla de resultado con los datos del formulario y la predicción
    return render_template('formulario.html', resultado=resultado, rendimiento_actual=rendimiento_actual)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
