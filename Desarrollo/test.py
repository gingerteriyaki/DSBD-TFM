import sys
import os

# Añadir el directorio 'scripts' al PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Ahora puedes importar el módulo
from download_data import download_files

# Llamar a la función para descargar los archivos
download_files()
