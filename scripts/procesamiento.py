from pathlib import Path
import pandas as pd
import psycopg 

# =========================
# Lectura del dataset 
# =========================

csv_file = Path(__file__).resolve().parent.parent / "data" / "dataset_agua.csv"

df = pd.read_csv(csv_file, sep=";")

print("Dataset original")
print(df)

# =========================
# Limpieza de datos
# =========================

# Reportar solos la medición de solidos disueltos que superen el ECA 50
df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
df= df[(df["Parámetro"] == 'Sólidos Suspendidos Totales') & (df['Valor']>=250)]

print("Dataset limpio")
print(df)

# =========================
# Exportación de dataset limpio
# =========================

# 1. Creamos un objeto Path con la ruta de destino
output_file = Path("output/dataset_agua_limpio.csv")

# 2. Creamos la carpeta 'output' si no existe (parents=True permite crear subcarpetas)
output_file.parent.mkdir(parents=True, exist_ok=True)

# 3. Crea una fila del encabezado
df.columns = df.columns.str.strip().str.lower()

# 4. Crea el archivo de salida
df.to_csv(output_file, sep=",", index=False)

print("Archivo exportado correctamente")

# =========================
# Conexión PostgreSQL
# =========================

conn = psycopg.connect(
    host="localhost",
    port="5433",    
    dbname="ambiental",
    user="postgres",
    password="12345678"
)
cursor = conn.cursor()

print("Conexión PostgreSQL exitosa")

# =========================
# Creación de tabla
# =========================

cursor.execute("DROP TABLE IF EXISTS dataset_agua_limpio;")

cursor.execute("""

CREATE TABLE IF NOT EXISTS dataset_agua_limpio (
    Etapa VARCHAR(100),
    Componente_ambiental VARCHAR(100),
    Nombre_del_punto VARCHAR(150),
    Este VARCHAR(50),
    Norte VARCHAR(50),
    Zona VARCHAR(50),
    Datum VARCHAR(50),
    Descripción_de_ubicación VARCHAR(250),
    Tipo_de_análisis VARCHAR(100),
    Fecha VARCHAR(50),
    Valor FLOAT,
    Parámetro VARCHAR(150),
    Unidad_de_medida VARCHAR(50)
)

""")

conn.commit()

print("Tabla creada correctamente")

# =========================
# Inserción de registros
# =========================

cursor.execute("DELETE FROM dataset_agua_limpio") 
conn.commit()

for index, row in df.iterrows():
    
    cursor.execute(
        """
        INSERT INTO dataset_agua_limpio 
        (Etapa,Componente_ambiental, Nombre_del_punto, Este, Norte,Zona, Datum,Descripción_de_ubicación,Tipo_de_análisis, Fecha, Valor, Parámetro, Unidad_de_medida)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            row['etapa'],
            row['componente ambiental'],
            row['nombre del punto'],
            row['este'],
            row['norte'],
            row['zona'],
            row['datum'],
            row['descripción de ubicación'],
            row['tipo de análisis'],
            row['fecha'],
            float(row['valor']),
            row['parámetro'],
            row['unidad de medida']
           
        )
    )
conn.commit()

print("Datos insertados correctamente")

# =========================
# Validación final
# =========================

cursor.execute("SELECT * FROM dataset_agua_limpio")

resultado = cursor.fetchall()
print(f"Total registros: {len(resultado)}")

print("Datos almacenados en PostgreSQL")

for fila in resultado:
    print(fila)

# =========================
# Cierre de conexión
# =========================

cursor.close()
conn.close()

print("Proceso finalizado correctamente")
