import requests

def get_siembra_data():
    url_siembra = "https://agricultura.gob.do/wp-content/uploads/2024/04/3.1-Superficie-Siembra-Mensual-Nacional-2000-2023.xlsx"
    response = requests.get(url_siembra)
    with open("consolidado_siembra.xlsx", "wb") as file:
        file.write(response.content)
    print("Datos de siembra mensual descargados.")

if __name__ == "__main__":
    get_siembra_data()
