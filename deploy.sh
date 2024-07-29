#!/bin/bash

# Activar el entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar scripts de preprocesamiento
python scripts/preprocess_historical_agricultural_data.py
python scripts/get_climate_data.py
python scripts/get_agriculture_data.py
python scripts/preprocess_siembra_data.py
python scripts/preprocess_produccion_data.py
python scripts/preprocess_cosecha_data.py

# Ejecutar script para calcular y subir proporciones mensuales
python scripts/calculate_and_upload_monthly_proportions.py

# Subir archivos procesados a DigitalOcean Spaces
python scripts/upload_to_spaces.py

echo "Deploy completado exitosamente"
