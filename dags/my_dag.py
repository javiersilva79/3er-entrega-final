from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import pandas as pd
import psycopg2

# Función para traer API - esta API la utilicé en la primer entrega
def consultar_api(url):
    try:
        # Realizar la solicitud GET a la URL de la API
        respuesta = requests.get(url)
        # Comprobar si la solicitud fue exitosa (código de estado 200)
        if respuesta.status_code == 200:
            # Si fue exitosa devolvemos los datos de la api en formato json
            return respuesta.json()
        else:
            # Si no fue exitosa se imprime el código de error
            print("Error al consultar la API:", respuesta.status_code)
            return None
    except Exception as e:
        # Manejar cualquier excepción que pueda ocurrir durante la solicitud
        print("Error de conexión:", e)
        return None

def my_task():
    # URL API. Elegí la 7timer debido a que es sencillo de entender. Simplifiqué los datos que trae para que aún sea mas facil de comprender
    url_api = "https://www.7timer.info/bin/api.pl?lon=-58.833&lat=-27.467&product=civillight&output=json"

    # Aquí llamo a la función con la url seleccionada de 7timer
    datos_api = consultar_api(url_api)

    # Compruebo si se trajo datos de la api o sino devuelvo error
    if datos_api:
        # Solo muestro en pantalla
        print("Datos de la API:", datos_api)
        # Cargo en un DataFrame la información de la api normalizada en json, con la librería pandas, y luego lo muestro en pantalla
        json_data = datos_api
        df = pd.json_normalize(json_data, 'dataseries')
        print(df)

        # Acá comienzo con la concexión a Redshift. Pongo en variables de entorno los datos de conexión
        host = os.environ['REDSHIFT_HOST']
        port = os.environ['REDSHIFT_PORT']
        dbname = os.environ['REDSHIFT_DBNAME']
        user = os.environ['REDSHIFT_USER']
        password = os.environ['REDSHIFT_PASSWORD']
        
        try:
            # Establezco la conexión y creo un cursor
            conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
            cur = conn.cursor()

            # Con el cursor creado ejecuto el SQL para crear la tabla. Donde creo 3 columnas adicionales a los datos devueltos por la API. Un identificador primario, una constante de la ciudad elegida para el clima y un Timestamp que nos da la fecha y hora actual cuando se inserta el dato
            cur.execute("""
            CREATE TABLE IF NOT EXISTS Javier_Prueba_API (
                id INTEGER PRIMARY KEY IDENTITY(1,1),
                fecha_hora TIMESTAMP DEFAULT GETDATE(),
                date INT,
                weather VARCHAR(20),
                max_temp INT,
                min_temp INT,
                wind_max INT
                )
            """)

            # Inserto los datos del dataframe en la tabla
            for index, row in df.iterrows():
                cur.execute("INSERT INTO Javier_Prueba_API (date, weather, max_temp, min_temp, wind_max) VALUES (%s, %s, %s, %s, %s)", 
                            (row['date'], row['weather'], row['temp2m.max'], row['temp2m.min'], row['wind10m_max']))

            # Confirmar la inserción
            conn.commit()

            # Y cierro la conexión
            cur.close()
            conn.close()
        except Exception as e:
            print("Error al conectar o insertar en la base de datos:", e)
    else:
        print("No se pudieron obtener datos de la API.")

# Definición del DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 5, 28, 0, 0),  # Fecha reciente
    'retries': 1,
    #'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'mi_dag_diario',
    default_args=default_args,
    description='Un DAG simple que se ejecuta diariamente.',
    schedule_interval='@daily',
    #schedule_interval='*/1 * * * *',  # Se ejecuta cada minuto
)

# Definición de la tarea
run_my_task = PythonOperator(
    task_id='run_my_task',
    python_callable=my_task,
    dag=dag,
)

run_my_task
