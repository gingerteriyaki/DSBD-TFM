import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os
import sklearn

print(f"scikit-learn version: {sklearn.__version__}")

# Leer los archivos de Excel y convertir las columnas a minúsculas
archivo_datos_agricolas = os.environ.get('DATOS_AGRICOLAS_PATH', 'data_agricola.xlsx')
datos_region_mes = pd.read_excel(archivo_datos_agricolas)
datos_region_mes.columns = datos_region_mes.columns.str.lower()

# Archivo con datos climáticos mensuales
archivo_datos_climaticos = os.environ.get('DATOS_CLIMATICOS_PATH', 'datos_climaticos.xlsx')
datos_climaticos = pd.read_excel(archivo_datos_climaticos)
datos_climaticos.columns = datos_climaticos.columns.str.lower()

# Unir los dos dataframes en función de las columnas comunes 'year', 'month' y 'region'
datos_combinados = pd.merge(datos_region_mes, datos_climaticos, on=['year', 'month', 'region'], how='inner')

# Agrupar correctamente utilizando las columnas individuales
datos_agrupados_numericos = datos_combinados.groupby(['year', 'month', 'region']).mean(numeric_only=True).reset_index()

# Crear nuevas características para una mayor generalización
datos_agrupados_numericos['temp_diff'] = datos_agrupados_numericos['max_temp'] - datos_agrupados_numericos['min_temp']
datos_agrupados_numericos['precip_per_humidity'] = datos_agrupados_numericos['precipitation'] / datos_agrupados_numericos['humidity']
datos_agrupados_numericos['siembra_vs_cosecha'] = datos_agrupados_numericos['siembra_mensual'] / datos_agrupados_numericos['cosecha_mensual']
datos_agrupados_numericos['produccion_vs_siembra'] = datos_agrupados_numericos['produccion_mensual'] / datos_agrupados_numericos['siembra_mensual']
datos_agrupados_numericos['rendimiento'] = datos_agrupados_numericos['produccion_mensual'] / datos_agrupados_numericos['siembra_mensual'] # Calcular el rendimiento

# Selección de características (variables independientes) y la variable objetivo
X = datos_agrupados_numericos[['year', 'month', 'region', 'siembra_mensual', 'cosecha_mensual', 
                               'precipitation', 'max_temp', 'min_temp', 'humidity', 'temp_diff', 
                               'precip_per_humidity', 'siembra_vs_cosecha', 'produccion_vs_siembra']]
y = datos_agrupados_numericos['rendimiento']

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Definir las transformaciones para las características numéricas y categóricas
numeric_features = ['year', 'month', 'siembra_mensual', 'cosecha_mensual', 
                    'precipitation', 'max_temp', 'min_temp', 'humidity',
                    'temp_diff', 'precip_per_humidity', 'siembra_vs_cosecha', 'produccion_vs_siembra']
categorical_features = ['region']

# Crear transformador de preprocesamiento
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(), categorical_features)
    ])

# Mejor configuración de hiperparámetros para Gradient Boosting Regressor
best_params_gbr = {
    'learning_rate': 0.1,
    'max_depth': 3,
    'min_samples_leaf': 6,
    'min_samples_split': 20,
    'n_estimators': 300,
    'subsample': 0.8,
    'random_state': 42
}

# Crear el modelo Gradient Boosting Regressor con los mejores parámetros
gbr_model = GradientBoostingRegressor(**best_params_gbr)

# Crear pipeline con preprocesamiento y modelo
pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                           ('model', gbr_model)])

# Entrenar el pipeline en el conjunto de datos de entrenamiento
pipeline.fit(X_train, y_train)

# Evaluar el modelo
y_pred = pipeline.predict(X_test)
print(f'Mean Squared Error: {mean_squared_error(y_test, y_pred)}')
print(f'Mean Absolute Error: {mean_absolute_error(y_test, y_pred)}')
print(f'R^2 Score: {r2_score(y_test, y_pred)}')

# Guardar el modelo entrenado
joblib.dump(pipeline, 'modelo_gbr.pkl')
print("Modelo guardado como 'modelo_gbr.pkl'")
