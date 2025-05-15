#!/bin/bash
set -e

# Initialize DB schema
airflow db upgrade

# Check if admin user exists
if ! airflow users list | grep admin; then
    echo "Creating admin user..."
    airflow users create \
      --username admin \
      --firstname Joy \
      --lastname Kimaiyo \
      --role Admin \
      --email joy.kimaiyo25@gmail.com \
      --password 'Timmy@2013'
else
    echo "Admin user already exists"
fi

# Start Airflow scheduler and webserver
airflow scheduler &

exec airflow webserver
