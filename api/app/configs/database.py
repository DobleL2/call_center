import pandas as pd
import pyodbc
import sqlite3
from dotenv import load_dotenv
from app.configs.query_loaders import load_query_from_file
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def get_sql_connection():
    """
    Establece una conexión con la base de datos SQL Server y la almacena en caché.

    Returns:
        pyodbc.Connection: Objeto de conexión a la base de datos.
    """
    try:
        # Obtener los parámetros de conexión desde las variables de entorno
        server = os.getenv('SQL_SERVER')
        database = os.getenv('SQL_DATABASE')
        username = os.getenv('SQL_USERNAME')
        password = os.getenv('SQL_PASSWORD')
        driver = os.getenv('SQL_DRIVER')

        # Crear la conexión
        connection = pyodbc.connect(
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        print("Conexión exitosa a la base de datos.")
        return connection
    except Exception as e:
        #st.write("Error al conectar con la base de datos:", e)
        return None

def copy_query_to_sqlite(sql_query, sqlite_db_path, sqlite_table_name):
    """
    Ejecuta una consulta SQL en la base remota y copia los resultados en una base de datos SQLite.
    Si la tabla ya existe, se elimina antes de copiar los nuevos datos.

    Args:
        sql_query (str): Consulta SQL a ejecutar en la base remota.
        sqlite_db_path (str): Ruta del archivo SQLite.
        sqlite_table_name (str): Nombre de la tabla en SQLite donde se copiarán los datos.
    """
    #try:
    # Conectar a la base de datos SQL Server
    sql_conn = get_sql_connection()
    #if not sql_conn:
    #    return
    
    # Ejecutar la consulta en la base remota
    sql_cursor = sql_conn.cursor()
    sql_cursor.execute(sql_query)
    rows = sql_cursor.fetchall()
    column_names = [desc[0] for desc in sql_cursor.description]

    # Conectar a la base de datos SQLite
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()

    # Eliminar la tabla si ya existe
    sqlite_cursor.execute(f"DROP TABLE IF EXISTS {sqlite_table_name}")
    sqlite_cursor.execute(f"DROP TABLE IF EXISTS mi_tabla")

    # Crear tabla en SQLite
    columns_definition = ", ".join([f"{col} TEXT" for col in column_names])
    create_table_query = f"CREATE TABLE {sqlite_table_name} ({columns_definition})"
    sqlite_cursor.execute(create_table_query)

    # Insertar los datos en SQLite
    placeholders = ", ".join(["?" for _ in column_names])
    insert_query = f"INSERT INTO {sqlite_table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
    sqlite_cursor.executemany(insert_query, rows)

    # Confirmar los cambios y cerrar las conexiones
    sqlite_conn.commit()
    print(f"Datos copiados exitosamente a la base local SQLite: {sqlite_db_path}")
    # except Exception as e:
    #     print("Error al copiar los datos:", e)
    # finally:
    #     if 'sql_cursor' in locals():
    #         sql_cursor.close()
    #     if 'sql_conn' in locals():
    #         sql_conn.close()
    #     if 'sqlite_conn' in locals():
    #         sqlite_conn.close()


# Ejemplo de uso
def update_local_database():
    # Define tu consulta SQL
    query = """
    SELECT
    jun.cod_junta,
    jun.id_junta,
    prov.cod_provincia,
    prov.nom_provincia AS provincia,
    isnull(
        circ.cod_circunscripcion,
        '0'
    ) AS cod_circunscripcion,
    isnull(
        circ.nom_circunscripcion,
        '-'
    ) AS circunscripcion,
    cant.cod_canton,
    cant.nom_canton AS canton,
    parr.cod_parroquia,
    parr.nom_parroquia AS parroquia,
    zon.cod_zona,
    zon.nom_zona AS zona,
    rec.cod_recinto,
    rec.nom_recinto AS recinto,
    junta,
    sexo,
    frm.cedula,
    frm.nombres,
    frm.apellidos,
    frm.correo,
    frm.operadora_celular,
    frm.num_celular,
    frm.referido,
    frm.parroquia_direccion
FROM
    provincia prov
    JOIN junta jun
    ON prov.cod_provincia = jun.cod_provincia
    LEFT JOIN circunscripcion circ
    ON jun.cod_provincia = circ.cod_provincia
    AND jun.cod_circunscripcion = circ.cod_circunscripcion
    JOIN canton cant
    ON cant.cod_canton = jun.cod_canton
    JOIN parroquia parr
    ON parr.cod_parroquia = jun.cod_parroquia
    JOIN zona zon
    ON parr.cod_parroquia = zon.cod_parroquia
    AND zon.cod_zona = jun.cod_zona
    JOIN recintos rec
    ON jun.cod_recinto = rec.cod_recinto
    LEFT JOIN formulario_control_electoral frm
	ON frm.cod_junta = jun.cod_junta
WHERE     
	jun.muestra = 0;
    """
    

    # Ruta de la base de datos SQLite y nombre de la tabla
    sqlite_path = "local_database.sqlite"
    sqlite_table = "data_estrategas"

    # Copiar datos de la base remota a SQLite
    copy_query_to_sqlite(query, sqlite_path, sqlite_table)


def upload_excel_to_sqlite(excel_file_path, sqlite_db_path, sqlite_table_name):
    """
    Carga los datos de un archivo Excel a una base de datos SQLite.

    Args:
        excel_file_path (str): Ruta del archivo Excel que contiene los datos.
        sqlite_db_path (str): Ruta del archivo SQLite donde se almacenarán los datos.
        sqlite_table_name (str): Nombre de la tabla en SQLite donde se copiarán los datos.
    """
    try:
        # Leer el archivo Excel en un DataFrame de pandas
        data = pd.read_excel(excel_file_path)

        # Conectar a la base de datos SQLite
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_cursor = sqlite_conn.cursor()

        # Eliminar la tabla si ya existe
        sqlite_cursor.execute(f"DROP TABLE IF EXISTS {sqlite_table_name}")

        # Crear la tabla en SQLite basada en las columnas del DataFrame
        columns_definition = ", ".join([f"{col} TEXT" for col in data.columns])
        create_table_query = f"CREATE TABLE {sqlite_table_name} ({columns_definition})"
        sqlite_cursor.execute(create_table_query)

        # Insertar los datos en SQLite
        data.to_sql(sqlite_table_name, sqlite_conn, if_exists='append', index=False)

        # Confirmar los cambios y cerrar la conexión
        sqlite_conn.commit()
        print(f"Datos del archivo Excel '{excel_file_path}' subidos exitosamente a la tabla '{sqlite_table_name}' en la base de datos '{sqlite_db_path}'.")
    except Exception as e:
        print("Error al cargar el archivo Excel a SQLite:", e)
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
            

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./local_database.sqlite"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False},execution_options={"sqlite_synchronous": "FULL"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()