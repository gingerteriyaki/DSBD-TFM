import pandas as pd
import os

# Definir las regiones según la provincia
regiones = {
    'Samaná': 'NORDESTE',
    'Barahona': 'SUROESTE',
    'Monte Plata': 'CENTRAL',
    'Santo Domingo': 'CENTRAL',
    'Puerto Plata': 'NORTE',
    'Monte Cristi': 'NOROESTE',
    'La Altagracia': 'ESTE',
    'Hato Mayor': 'ESTE',
    'San José de Ocoa': 'SUR',
    'Santiago': 'NORTE',
    'San Cristóbal': 'CENTRAL',
    'María Trinidad Sánchez': 'NORDESTE',
    'Independencia': 'SUROESTE',
    'La Romana': 'ESTE'
}

# Cargar el archivo Excel desde una ruta proporcionada como variable de entorno
archivo = os.environ.get('CLIMATE_DATA_PATH', 'base_de_datos_clima.xlsx')
df = pd.read_excel(archivo, sheet_name=1)

# Filtrar los datos a partir del año 2011
df = df[df['Año'] >= 2011]

# Asignar la región según la provincia
df['Región'] = df['Provincia'].map(regiones)

# Pivotar la tabla para convertir las variables en columnas
df_pivot = df.pivot_table(index=['Provincia', 'Estación', 'Año', 'Mes', 'Región'], columns='Variable', values='Valor').reset_index()

# Renombrar las columnas para que coincidan con el formato deseado
df_pivot.columns.name = None  # Eliminar el nombre de las columnas
df_pivot = df_pivot.rename(columns={'Año': 'YEAR', 'Mes': 'MONTH'})

# Reorganizar las columnas en el formato deseado
columnas_finales = ['YEAR', 'MONTH', 'Región'] + [col for col in df_pivot.columns if col not in ['YEAR', 'MONTH', 'Región', 'Provincia', 'Estación']]
df_pivot = df_pivot[['YEAR', 'MONTH', 'Región'] + columnas_finales]

# Guardar los datos preprocesados en un nuevo archivo Excel
output_path = os.environ.get('PROCESSED_CLIMATE_DATA_PATH', 'datos_climaticos.xlsx')
df_pivot.to_excel(output_path, index=False)

print(f"Datos climáticos preprocesados y guardados en {output_path}")
