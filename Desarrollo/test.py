import pandas as pd
from dotenv import load_dotenv
import os
import boto3

# Cargar variables de entorno
load_dotenv()

def calcular_proporciones_distribuidas(df_mensual, df_consolidado, columna):
    # Imprimir las columnas del DataFrame para depuración
    print("Columnas de df_consolidado:", df_consolidado.columns)
    print("Primeras filas de df_consolidado:", df_consolidado.head())

    # Inicializar un DataFrame vacío para almacenar los resultados
    df_resultado = pd.DataFrame()

    # Iterar sobre cada año en el DataFrame mensual
    for year in df_mensual['YEAR'].unique():
        # Filtrar los datos del año en cuestión
        df_consolidado_anual = df_consolidado[df_consolidado['YEAR'] == year]
        df_mensual_anual = df_mensual[df_mensual['YEAR'] == year]

        for region in df_mensual_anual['REGION'].unique():
            # Filtrar los datos de la región en cuestión
            df_consolidado_region = df_consolidado_anual[df_consolidado_anual['REGION'] == region]
            df_mensual_region = df_mensual_anual[df_mensual_anual['REGION'] == region]

            if not df_consolidado_region.empty:
                # Obtener el valor consolidado anual
                valor_anual = df_consolidado_region[columna].values[0]

                # Calcular la proporción mensual
                df_mensual_region[f'{columna}_PROPORCION'] = df_mensual_region[columna] / valor_anual

                # Agregar los datos al DataFrame de resultados
                df_resultado = pd.concat([df_resultado, df_mensual_region])

    return df_resultado

def main():
    # Cargar los datos desde archivos Excel
    ruta = 'data/'
    siembra_mensual = pd.read_excel(ruta + 'datos_siembra_mensuales.xlsx')
    cosecha_mensual = pd.read_excel(ruta + 'datos_cosecha_mensuales.xlsx')
    produccion_mensual = pd.read_excel(ruta + 'datos_produccion_mensuales.xlsx')
    agricola_consolidado = pd.read_excel(ruta + 'consolidado_agricola.xlsx')

    # Calcular las proporciones distribuidas
    siembra_resultado = calcular_proporciones_distribuidas(siembra_mensual, agricola_consolidado, 'SIEMBRA')
    cosecha_resultado = calcular_proporciones_distribuidas(cosecha_mensual, agricola_consolidado, 'COSECHA')
    produccion_resultado = calcular_proporciones_distribuidas(produccion_mensual, agricola_consolidado, 'PRODUCCION')

    # Guardar los resultados en un nuevo archivo Excel
    output_path = ruta + 'datos_mensuales_por_region.xlsx'
    with pd.ExcelWriter(output_path) as writer:
        siembra_resultado.to_excel(writer, sheet_name='Siembra', index=False)
        cosecha_resultado.to_excel(writer, sheet_name='Cosecha', index=False)
        produccion_resultado.to_excel(writer, sheet_name='Producción', index=False)

    print(f"Datos mensuales por región guardados en {output_path}")

if __name__ == "__main__":
    main()