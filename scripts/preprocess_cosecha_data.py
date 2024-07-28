import pandas as pd
import re
import os

# Función para eliminar acentos
def eliminar_acentos(texto):
    acentos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
               'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
    for acento, letra in acentos.items():
        texto = texto.replace(acento, letra)
    return texto

# Función para normalizar los nombres de las hojas y etiquetas
def normalizar(texto):
    if isinstance(texto, str):
        texto = eliminar_acentos(texto)  # Elimina acentos
        texto = texto.lower()
        texto = re.sub(r'[^a-z0-9\s]', '', texto)  # Elimina caracteres especiales
    return texto

# Función para buscar el producto en las filas cercanas
def buscar_producto(df, keyword):
    for idx in range(len(df)):
        if re.search(keyword, normalizar(str(df.iloc[idx, 0]))):
            return idx
    return -1

# Cargar el archivo Excel desde una ruta proporcionada como variable de entorno
archivo = os.environ.get('COSECHA_DATA_PATH', 'consolidado_cosecha.xlsx')
excel = pd.ExcelFile(archivo)

# Definir las hojas que vamos a procesar (solo las del año 2011 en adelante)
hojas = [hoja for hoja in excel.sheet_names if any(str(año) in hoja for año in range(2011, 2024))]

# Crear un diccionario para almacenar los datos extraídos
datos = []

# Procesar cada hoja
for hoja in hojas:
    df = pd.read_excel(archivo, sheet_name=hoja)
    year = int(re.search(r'\d{4}', hoja).group())

    # Normalizar la columna de producto
    df.iloc[:, 0] = df.iloc[:, 0].apply(lambda x: normalizar(str(x)))

    # Buscar la fila que contiene el producto "platano"
    idx_producto = buscar_producto(df, 'platano')
    if idx_producto == -1:
        continue

    # Extraer los datos de los meses (asumiendo que las columnas de meses están en los índices 1 a 12)
    row = df.iloc[idx_producto, 1:13]


    # Agregar los datos al diccionario
    datos.append({
        'YEAR': year,
        '01': row[0],
        '02': row[1],
        '03': row[2],
        '04': row[3],
        '05': row[4],
        '06': row[5],
        '07': row[6],
        '08': row[7],
        '09': row[8],
        '10': row[9],
        '11': row[10],
        '12': row[11],
        'TOTAL': row.sum()
    })

# Convertir los datos a DataFrame para su análisis
datos_df = pd.DataFrame(datos)

# Guardar los datos preprocesados en un nuevo archivo Excel
output_path = os.environ.get('PROCESSED_COSECHA_DATA_PATH', 'datos_cosecha_mensuales.xlsx')
datos_df.to_excel(output_path, index=False)

print(f"Datos de cosecha preprocesados y guardados en {output_path}")
