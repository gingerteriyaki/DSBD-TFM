from flask import Flask, request, render_template
import joblib
import numpy as np

app = Flask(__name__)

# Intenta cargar el modelo al iniciar la aplicación
try:
    model = joblib.load('modelo_gbr.pkl')
except FileNotFoundError:
    model = None
    print("Error: El archivo del modelo no se encontró.")
except EOFError:
    model = None
    print("Error: El archivo del modelo está dañado.")
except Exception as e:
    model = None
    print(f"Error inesperado al cargar el modelo: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_rendimiento():
    if model is None:
        return "Error: El modelo no está disponible.", 500
    
    try:
        # Recoger datos del formulario
        year = int(request.form.get('year'))
        month = int(request.form.get('month'))
        region = request.form.get('region')
        siembra_mensual = float(request.form.get('siembra_mensual'))
        cosecha_mensual = float(request.form.get('cosecha_mensual'))
        produccion_mensual = float(request.form.get('produccion_mensual'))
        precipitation = float(request.form.get('precipitation') or 0)
        max_temp = float(request.form.get('max_temp') or 0)
        min_temp = float(request.form.get('min_temp') or 0)
        humidity = float(request.form.get('humidity') or 0)
        
        # Crear un array con los datos de entrada
        input_features = np.array([[year, month, siembra_mensual, cosecha_mensual, produccion_mensual,
                                    precipitation, max_temp, min_temp, humidity]])
        
        # Realizar la predicción
        prediction = model.predict(input_features)
        
        # Enviar el resultado a la plantilla
        return render_template('index.html', resultado={'prediccion_rendimiento': prediction[0]}, rendimiento_actual=produccion_mensual)
    
    except Exception as e:
        print(f"Error en la predicción: {e}")
        return "Error al realizar la predicción.", 500

if __name__ == '__main__':
    app.run(debug=True)