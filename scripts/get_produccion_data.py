import requests

def get_produccion_data():
    url_produccion = "https://agricultura.gob.do/wp-content/uploads/2024/04/5.1.1-Produccion-Mensual-Nacional-2000-2023-En-QQ.-Mill.-y-Rac-2.xls"
    response = requests.get(url_produccion)
    with open("consolidado_produccion.xlsx", "wb") as file:
        file.write(response.content)
    print("Datos de produccion mensual descargados.")

if __name__ == "__main__":
    get_produccion_data()
