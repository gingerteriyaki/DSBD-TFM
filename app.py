from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Ruta para servir la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar las predicciones
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Obtener datos del formulario
        data = request.get_json()
        
        # Definir los campos necesarios y opcionales
        essential_fields = ['nombre', 'apellido', 'year', 'month', 'region', 'siembra_mensual', 'cosecha_mensual', 'produccion_mensual']
        optional_fields = ['precipitation', 'max_temp', 'min_temp', 'humidity']
        
        # Verificar que los campos esenciales están presentes
        for field in essential_fields:
            if field not in data:
                return jsonify({'error': f"Falta campo esencial: {field}"}), 400
        
        # Construir la URL del API
        base_url = "https://sea-lion-app-j62p4.ondigitalocean.app/predict"
        params = {
            'year': data.get('year'),
            'month': data.get('month'),
            'region': data.get('region'),
            'siembra_mensual': data.get('siembra_mensual'),
            'cosecha_mensual': data.get('cosecha_mensual'),
            'produccion_mensual': data.get('produccion_mensual'),
            'precipitation': data.get('precipitation', 0),
            'max_temp': data.get('max_temp', 0),
            'min_temp': data.get('min_temp', 0),
            'humidity': data.get('humidity', 0)
        }
        
        # Realizar la solicitud al API
        response = requests.get(base_url, params=params)
        
        # Manejar la respuesta del API
        if response.status_code == 200:
            prediccion = response.json()
            return jsonify({'rendimiento_predicho': prediccion.get('prediccion_rendimiento')})
        else:
            return jsonify({'error': 'Error al realizar la predicción'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
