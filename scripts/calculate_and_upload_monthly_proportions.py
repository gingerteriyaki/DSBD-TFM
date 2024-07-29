import pandas as pd
import boto3
import os
from dotenv import load_dotenv

def cargar_variables_entorno():
    load_dotenv()
    access_key = os.getenv('SPACES_ACCESS_KEY_ID')
    secret_key = os.getenv('SPACES_SECRET_ACCESS_KEY')
    return access_key, secret_key

def configurar_cliente_boto3(access_key, secret_key):
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='fra1',
                            endpoint_url='https://climaplatano.fra1.digitaloceanspaces.com',
                            aws_access_key_id=os.environ['SPACES_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['SPACES_SECRET_ACCESS_KEY'])
    return client

def leer_archivos():
    siembra_mensual = pd.read_excel('datos_siembra_mensuales.xlsx')
    produccion_mensual = pd.read_excel('datos_produccion_mensuales.xlsx')
    cosecha_mensual = pd.read_excel('datos_cosecha_mensuales.xlsx')
    agricola_consolidado = pd.read_excel('consolidado_agricola_general.xlsx')
    return siembra_mensual, produccion_mensual, cosecha_mensual, agricola_consolidado

def calcular_totales_anuales(df):
    df['TOTAL'] = df.iloc[:, 1:].sum(axis=1)
    return df

def calcular_proporciones_distribuidas(df_mensual, df_consolidado, columna):
    df_resultado = pd.DataFrame()
    for year in df_mensual['YEAR']:
        total_anual_nacional = df_mensual.loc[df_mensual['YEAR'] == year, 'TOTAL'].values[0]
        proporciones_mensuales = df_mensual[df_mensual['YEAR'] == year].iloc[:, 1:-1].div(total_anual_nacional).values[0]
        df_consolidado_anual = df_consolidado[df_consolidado['YEAR'] == year]

        for idx, row in df_consolidado_anual.iterrows():
            valores_mensuales = proporciones_mensuales * row[columna]
            for mes, valor in enumerate(valores_mensuales, start=1):
                df_resultado = pd.concat([df_resultado, pd.DataFrame([{
                    'YEAR': year,
                    'REGION': row['REGION'],
                    'MONTH': f"{mes:02d}",
                    f'{columna}_MENSUAL': valor
                }])], ignore_index=True)
    return df_resultado

def generar_archivo_final(siembra_resultado, produccion_resultado, cosecha_resultado):
    resultado_final = siembra_resultado.merge(
        cosecha_resultado, on=['YEAR', 'REGION', 'MONTH']
    ).merge(
        produccion_resultado, on=['YEAR', 'REGION', 'MONTH']
    )
    archivo_final = 'datos_mensuales_por_region.xlsx'
    resultado_final.to_excel(archivo_final, index=False)
    return archivo_final

def subir_archivo(client, archivo_final):
    bucket_name = 'climaplatano'
    object_name = 'data_agricola.xlsx'
    client.upload_file(archivo_final, bucket_name, object_name)
    print(f"Archivo {archivo_final} subido a DigitalOcean Spaces como {object_name}")

def main():
    access_key, secret_key = cargar_variables_entorno()
    client = configurar_cliente_boto3(access_key, secret_key)
    siembra_mensual, produccion_mensual, cosecha_mensual, agricola_consolidado = leer_archivos()

    siembra_mensual = calcular_totales_anuales(siembra_mensual)
    produccion_mensual = calcular_totales_anuales(produccion_mensual)

    siembra_resultado = calcular_proporciones_distribuidas(siembra_mensual, agricola_consolidado, 'SIEMBRA')
    produccion_resultado = calcular_proporciones_distribuidas(produccion_mensual, agricola_consolidado, 'PRODUCCION')
    cosecha_resultado = calcular_proporciones_distribuidas(cosecha_mensual, agricola_consolidado, 'COSECHA')

    archivo_final = generar_archivo_final(siembra_resultado, produccion_resultado, cosecha_resultado)
    subir_archivo(client, archivo_final)

if __name__ == "__main__":
    main()
