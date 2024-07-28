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
def buscar_producto(df, start_idx, keyword):
    for idx in range(start_idx, len(df)):
        if re.search(keyword, normalizar(str(df.iloc[idx, 0]))):
            return idx
    return -1

# Cargar el archivo Excel desde una ruta proporcionada como variable de entorno
archivo = os.environ.get('HISTORICAL_DATA_PATH', 'consolidado_agricola.xlsx')
excel = pd.ExcelFile(archivo)

# Definir las hojas que vamos a procesar (solo las del año 2011 en adelante)
hojas = [hoja for hoja in excel.sheet_names if re.match(r'consolidado', normalizar(hoja)) and any(str(año) in hoja for año in range(2011, 2024))]

# Crear un diccionario para almacenar los datos extraídos
datos = []

# Procesar cada hoja
for hoja in hojas:
    df = pd.read_excel(archivo, sheet_name=hoja)
    year = int(re.search(r'\d{4}', hoja).group())

    idx = 0
    registros = {'siembra': {}, 'cosecha': {}, 'produccion': {}}
    
    for seccion in ['siembra', 'cosecha', 'produccion']:
        # Buscar la fila que contiene la sección actual
        idx = buscar_producto(df, idx, seccion)
        if idx == -1:
            continue

        # Normalizar la columna de producto
        df.iloc[:, 0] = df.iloc[:, 0].apply(lambda x: normalizar(str(x)))

        # Buscar la fila que contiene el producto "platano"
        idx_producto = buscar_producto(df, idx, 'platano')
        if idx_producto == -1:
            continue

        # Extraer los datos de las columnas B a I (índices 1 a 8)
        for col_idx, region in enumerate(['NORTE', 'NORDESTE', 'NOROESTE', 'NORCENTRAL', 'CENTRAL', 'SUR', 'SUROESTE', 'ESTE']):
            registros[seccion][region] = df.iloc[idx_producto, col_idx + 1]

    # Consolidar los registros para cada región
    for region in ['NORTE', 'NORDESTE', 'NOROESTE', 'NORCENTRAL', 'CENTRAL', 'SUR', 'SUROESTE', 'ESTE']:
        cosecha_valor = registros['cosecha'].get(region)

        datos.append({
            'YEAR': year,
            'REGION': region,
            'SIEMBRA': registros['siembra'].get(region),
            'COSECHA': cosecha_valor,
            'PRODUCCION': registros['produccion'].get(region)
        })

# Convertir los datos a DataFrame para su análisis
datos_df = pd.DataFrame(datos)

# Ordenar las columnas según el formato deseado
datos_df = datos_df[['YEAR', 'REGION', 'SIEMBRA', 'COSECHA', 'PRODUCCION']]

# Guardar los datos extraídos en un nuevo archivo Excel
output_path = os.environ.get('PROCESSED_DATA_PATH', 'datos_agricola_consolidados_mod.xlsx')
datos_df.to_excel(output_path, index=False)

print(f"Datos preprocesados y guardados en {output_path}")
