import requests

def get_agriculture_data():
    url_agricultura = "https://agricultura.gob.do/wp-content/uploads/2019/04/2.2-CONSOLIDADO-REGIONAL-SC-y-P-DE-PRODUCTOS-AGRICOLAS-2000-2022.xlsx"
    response = requests.get(url_agricultura)
    with open("consolidado_agricola.xlsx", "wb") as file:
        file.write(response.content)
    print("Datos agrícolas descargados.")

if __name__ == "__main__":
    get_agriculture_data()
