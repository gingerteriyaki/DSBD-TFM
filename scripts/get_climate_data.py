import requests
import pandas as pd

# URLs de los archivos XLSX
urls = {
    "precipitation": "https://cckpapi.worldbank.org/cckp/v1/cru-x0.5_timeseries_pr_timeseries_monthly_1901-2022_mean_historical_cru_ts4.07_mean/DOM,DOM.721108,DOM.721109,DOM.721110,DOM.721111,DOM.7236858,DOM.721113,DOM.721114,DOM.721118,DOM.721115,DOM.7236854,DOM.721116,DOM.721117,DOM.721119,DOM.721120,DOM.721121,DOM.7236855,DOM.721122,DOM.7236856,DOM.721123,DOM.721124,DOM.721125,DOM.721126,DOM.721127,DOM.721128,DOM.7236857,DOM.721129,DOM.721130,DOM.721131,DOM.721132,DOM.721133,DOM.721112,DOM.721134?_format=xlsx",
    "max_temp": "https://cckpapi.worldbank.org/cckp/v1/cru-x0.5_timeseries_tasmax_timeseries_monthly_1901-2022_mean_historical_cru_ts4.07_mean/DOM,DOM.721108,DOM.721109,DOM.721110,DOM.721111,DOM.7236858,DOM.721113,DOM.721114,DOM.721118,DOM.721115,DOM.7236854,DOM.721116,DOM.721117,DOM.721119,DOM.721120,DOM.721121,DOM.7236855,DOM.721122,DOM.7236856,DOM.721123,DOM.721124,DOM.721125,DOM.721126,DOM.721127,DOM.721128,DOM.7236857,DOM.721129,DOM.721130,DOM.721131,DOM.721132,DOM.721133,DOM.721112,DOM.721134?_format=xlsx",
    "min_temp": "https://cckpapi.worldbank.org/cckp/v1/cru-x0.5_timeseries_tasmin_timeseries_monthly_1901-2022_mean_historical_cru_ts4.07_mean/DOM,DOM.721108,DOM.721109,DOM.721110,DOM.721111,DOM.7236858,DOM.721113,DOM.721114,DOM.721118,DOM.721115,DOM.7236854,DOM.721116,DOM.721117,DOM.721119,DOM.721120,DOM.721121,DOM.7236855,DOM.721122,DOM.7236856,DOM.721123,DOM.721124,DOM.721125,DOM.721126,DOM.721127,DOM.721128,DOM.7236857,DOM.721129,DOM.721130,DOM.721131,DOM.721132,DOM.721133,DOM.721112,DOM.721134?_format=xlsx",
    "humidity": "https://cckpapi.worldbank.org/cckp/v1/era5-x0.25_timeseries_hurs_timeseries_monthly_1950-2022_mean_historical_era5_x0.25_mean/DOM,DOM.721108,DOM.721109,DOM.721110,DOM.721111,DOM.7236858,DOM.721113,DOM.721114,DOM.721118,DOM.721115,DOM.7236854,DOM.721116,DOM.721117,DOM.721119,DOM.721120,DOM.721121,DOM.7236855,DOM.721122,DOM.7236856,DOM.721123,DOM.721124,DOM.721125,DOM.721126,DOM.721127,DOM.721128,DOM.7236857,DOM.721129,DOM.721130,DOM.721131,DOM.721132,DOM.721133,DOM.721112,DOM.721134?_format=xlsx"
}

# Diccionario de regiones según el nombre
regions = {
    'Azua': 'SUR',
    'Baoruco': 'SUROESTE',
    'Barahona': 'SUROESTE',
    'Dajabon': 'NOROESTE',
    'Santo Domingo': 'CENTRAL',
    'Duarte': 'NORDESTE',
    'El Seibo': 'ESTE',
    'Espaillat': 'NORCENTRAL',
    'Independencia': 'SUROESTE',
    'La Altagracia': 'ESTE',
    'Elias Pina': 'SUROESTE',
    'La Romana': 'ESTE',
    'La Vega': 'NORCENTRAL',
    'Maria Trinidad Sanches': 'NORDESTE',
    'Monte Cristi': 'NOROESTE',
    'Pedernales': 'SUROESTE',
    'Peravia': 'SUR',
    'Puerto Plata': 'NORTE',
    'Salcedo': 'NORCENTRAL',
    'Samana': 'NORDESTE',
    'San Cristobal': 'CENTRAL',
    'San Juan': 'SUROESTE',
    'San Pedro de Macoris': 'ESTE',
    'Sanchez Ramirez': 'NORCENTRAL',
    'Santiago': 'NORTE',
    'Santiago Rodriguez': 'NOROESTE',
    'Valverde': 'NOROESTE',
    'Hato Mayor': 'ESTE',
    'Monsenor Nouel': 'NORCENTRAL',
    'Monte Plata': 'CENTRAL',
    'San José de Ocoa': 'SUR',
    'Distrito Nacional': 'CENTRAL'
}

# Descargar y transformar los datos
def download_and_transform(url, value_name):
    response = requests.get(url)
    if response.status_code == 200:
        df = pd.read_excel(response.content)
        df_melted = df.melt(id_vars=["code", "name"], var_name="year_month", value_name=value_name)
        df_melted[['year', 'month']] = df_melted['year_month'].str.split('-', expand=True)
        df_melted.drop(columns=['year_month', 'code'], inplace=True)
        df_melted.rename(columns={'name': 'provincia'}, inplace=True)
        df_melted = df_melted[df_melted['provincia'] != 'Dominican Republic']
        df_melted = df_melted[df_melted['year'].astype(int) >= 2011]
        df_melted['region'] = df_melted['provincia'].map(regions)
        df_melted = df_melted[['year', 'month', 'region', 'provincia', value_name]]
        return df_melted
    else:
        print(f"Failed to download file from {url}. Status code: {response.status_code}")
        return pd.DataFrame()

if __name__ == "__main__":
    df_precipitation = download_and_transform(urls["precipitation"], "precipitation")
    df_max_temp = download_and_transform(urls["max_temp"], "max_temp")
    df_min_temp = download_and_transform(urls["min_temp"], "min_temp")
    df_humidity = download_and_transform(urls["humidity"], "humidity")

    df_combined = df_precipitation
    df_combined = df_combined.merge(df_max_temp, on=["year", "month", "region", "provincia"], how="outer")
    df_combined = df_combined.merge(df_min_temp, on=["year", "month", "region", "provincia"], how="outer")
    df_combined = df_combined.merge(df_humidity, on=["year", "month", "region", "provincia"], how="outer")

    # Guardar el DataFrame combinado en un archivo Excel temporal
    output_file_path = 'datos_climaticos.xlsx'
    df_combined.to_excel(output_file_path, index=False)
    print(f"Combined data saved to {output_file_path}")
