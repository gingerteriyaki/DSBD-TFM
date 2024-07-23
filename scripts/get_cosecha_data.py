import requests

def get_cosecha_data():
    url_cosecha = "https://agricultura.gob.do/wp-content/uploads/2024/06/4.1-Superficie-Cosechada-Mensual-a-Nivel-Nacional-2000-2023.xls"
    response = requests.get(url_cosecha)
    with open("consolidado_cosecha.xlsx", "wb") as file:
        file.write(response.content)
    print("Datos de cosecha mensual descargados.")

if __name__ == "__main__":
    get_cosecha_data()
