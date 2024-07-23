import requests

def get_climate_data():
    url_clima = "https://www.one.gob.do/media/1tkdwfzq/base-de-datos_-atm%C3%B3sfera-y-clima-1960-2023.xlsx"
    response = requests.get(url_clima)
    with open("base_de_datos_clima.xlsx", "wb") as file:
        file.write(response.content)
    print("Datos climáticos descargados.")

if __name__ == "__main__":
    get_climate_data()
