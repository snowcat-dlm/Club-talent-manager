#!/bin/bash
set -e

echo "Starting entrypoint script..."
echo "1: Changing to the project directory(/talentManager/)..."
if [ ! -d "/workspace/talentManager" ]; then
  echo "!entrypoint.sh Error! /workspace/talentManager does not exist"
  ls -la /workspace
  exit 1
fi
cd /workspace/talentManager

echo "2: Running make migrations..."
python manage.py makemigrations

echo "3: Running migrations..."
python manage.py migrate

# Webサーバーを自動起動する場合は以下のコメントを外してください
# echo "4: Starting server..."
# python manage.py runserver
