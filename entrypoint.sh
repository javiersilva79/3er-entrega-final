#!/bin/bash

# Inicializar la base de datos de Airflow
airflow db init

# Crear usuario admin si no existe
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com || true

# Ejecutar el servidor web de Airflow en el puerto 8081
airflow scheduler &
exec airflow webserver --port 8081