import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# Descargar el HTML
url = "https://ycharts.com/companies/TSLA/revenues"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Intentar obtener la página varias veces en caso de error
for i in range(5):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        datos_html = response.text
        soup = BeautifulSoup(datos_html, 'html.parser')
        break
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"Request failed with status code {e.response.status_code}. Retrying...")
            headers['User-Agent'] = headers['User-Agent'].replace('Chrome/91.0.4472.124', f'Chrome/{random.randint(50, 60)}.{random.randint(0, 100)}.{random.randint(0, 100)}')
        else:
            raise

# Encontrar todas las tablas en la página
tables = soup.find_all("table")
tables

# Identificar el índice de la tabla correcta
table_index = None
for index, table in enumerate(tables):
    if "Date" in str(table) and "Value" in str(table):
        table_index = index
        break

if table_index is None:
    raise ValueError("No se encontró la tabla con los datos de ingresos trimestrales.")


# Crear un DataFrame
tesla_revenue = pd.DataFrame(columns=["Date", "Revenue"])
for row in tables[table_index].find_all("tr"):
    cols = row.find_all("td")
    if len(cols) == 2:
        Date = cols[0].text.strip()
        Revenue = cols[1].text.strip().replace("B", "B").replace("M", "M")
        tesla_revenue = pd.concat([tesla_revenue, pd.DataFrame({
            "Date": [Date],
            "Revenue": [Revenue]
        })], ignore_index=True)

# Mostrar las primeras filas del DataFrame
print(tesla_revenue.head())

#Limpieza de los datos
import pandas as pd
import numpy as np

print("DataFrame inicial:")
print(tesla_revenue.head())

# Limpiar los datos
# Eliminar el símbolo "$" y las comas, convertir a valores numéricos
def clean_revenue(value):
    if pd.isna(value) or value.strip() == "":
        return np.nan
    # Remover caracteres no numéricos excepto el punto decimal y la letra 'B' o 'M'
    value = value.replace('B', '').replace('M', '').strip()
    value = value.replace(',', '')
    # Convertir a float, agregando el sufijo 'B' como multiplicador
    if 'B' in value:
        return float(value) * 1e9
    elif 'M' in value:
        return float(value) * 1e6
    else:
        return float(value)

# Aplicar la función de limpieza a la columna 'Revenue'
tesla_revenue['Revenue'] = tesla_revenue['Revenue'].apply(clean_revenue)

# Eliminar filas vacías o con datos no válidos en la columna 'Revenue'
tesla_revenue = tesla_revenue.dropna(subset=['Revenue'])

# Ordenar por fecha (si es necesario) y restablecer el índice
tesla_revenue = tesla_revenue.sort_values(by="Date").reset_index(drop=True)

# Mostrar el DataFrame limpio
print("DataFrame limpio:")
print(tesla_revenue.head())

# Almacenado de datos en SQLite
import sqlite3
import pandas as pd

# Crear conexión a la BD SQLite
conn = sqlite3.connect('tesla_revenues.db')

# Crear cursor para ejecutar comandos SQL
cur = conn.cursor()

# Crear la tabla en la BD
cur.execute('''
CREATE TABLE IF NOT EXISTS tesla_revenues (
    Date TEXT PRIMARY KEY,
    Revenue REAL
)
''')

# Comprobar tabla
cur.execute("PRAGMA table_info(tesla_revenues)")
print("Tabla 'tesla_revenues' en la base de datos:")
print(cur.fetchall())

# Insertar datos en la tabla desde el DataFrame
data_to_insert = tesla_revenue.to_records(index=False).tolist()

# Insertar datos en la tabla
cur.executemany('''
INSERT OR REPLACE INTO tesla_revenues (Date, Revenue)
VALUES (?, ?)
''', data_to_insert)

# Confirmar los cambios (commit)
conn.commit()

# Cerrar la conexión
conn.close()

print("Datos almacenados en la base de datos SQLite con éxito.")

# Visualización de los datos

# Grafico 1 de Linea

import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos desde la BD
conn = sqlite3.connect('tesla_revenues.db')
tesla_revenue = pd.read_sql_query("SELECT * FROM tesla_revenues", conn)
conn.close()

# Convertir la columna 'Date' a tipo datetime y 'Revenue' a tipo numérico
tesla_revenue['Date'] = pd.to_datetime(tesla_revenue['Date'], format='%B %d, %Y')
tesla_revenue['Revenue'] = tesla_revenue['Revenue'].apply(pd.to_numeric, errors='coerce')

# Ordenar los datos por fecha
tesla_revenue = tesla_revenue.sort_values('Date')

# Graficar
plt.figure(figsize=(12, 6))
plt.plot(tesla_revenue['Date'], tesla_revenue['Revenue'], marker='o', linestyle='-', color='b')
plt.title('Tesla Revenue Over Time')
plt.xlabel('Date')
plt.ylabel('Revenue (in billions)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Grafico 2 Barras
plt.figure(figsize=(12, 6))
plt.bar(tesla_revenue['Date'].dt.strftime('%Y-%m'), tesla_revenue['Revenue'], color='skyblue')
plt.title('Tesla Revenue by Quarter')
plt.xlabel('Date')
plt.ylabel('Revenue (in billions)')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Grafico 3 de Area
plt.figure(figsize=(12, 6))
plt.fill_between(tesla_revenue['Date'], tesla_revenue['Revenue'], color='skyblue', alpha=0.4)
plt.plot(tesla_revenue['Date'], tesla_revenue['Revenue'], marker='o', color='b', linestyle='-')
plt.title('Tesla Revenue Area Plot')
plt.xlabel('Date')
plt.ylabel('Revenue (in billions)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()