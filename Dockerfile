# Usar una imagen base de Python slim para mantener el contenedor ligero
FROM python:3.9-slim

# Establecer variables de entorno
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/airflow.db

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        libffi-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instalar Apache Airflow
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install apache-airflow
#RUN pip install --upgrade pendulum==2.1.2
RUN pip install -r /requirements.txt

# Crear el directorio de Airflow
RUN mkdir -p ${AIRFLOW_HOME}

# Copiar los DAGs al directorio de Airflow
COPY dags ${AIRFLOW_HOME}/dags

# Copiar el script de inicio
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponer el puerto 8081
EXPOSE 8081

# Comando para ejecutar el script de inicio
ENTRYPOINT ["/entrypoint.sh"]
