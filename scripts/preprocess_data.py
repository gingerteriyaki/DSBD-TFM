import pandas as pd

def preprocess_data():
    # Cargar archivos XLS
    df_clima = pd.read_excel("base_de_datos_clima.xlsx")
    df_agricultura = pd.read_excel("consolidado_agricola.xlsx")

    # Preprocesamiento básico
    df_clima_cleaned = df_clima.dropna()  # Ejemplo de limpieza
    df_agricultura_cleaned = df_agricultura.dropna()

    # Guardar como CSV
    df_clima_cleaned.to_csv("base_de_datos_clima_cleaned.csv", index=False)
    df_agricultura_cleaned.to_csv("consolidado_agricola_cleaned.csv", index=False)
    print("Datos preprocesados y guardados como CSV.")

if __name__ == "__main__":
    preprocess_data()
