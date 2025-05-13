FROM apache/airflow:2.7.3-python3.9

USER root
RUN apt-get update && \
    apt-get install -y default-mysql-client gcc && \
    rm -rf /var/lib/apt/lists/*

USER airflow
RUN pip install --no-cache-dir pymysql mysql-connector-python

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scraper.py ${AIRFLOW_HOME}/dags/