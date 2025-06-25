#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate

echo "Loading fixture data..."
python manage.py loaddata initial_data

echo "Starting Gunicorn..."
exec gunicorn your_project.wsgi:application --bind 0.0.0.0:8000
