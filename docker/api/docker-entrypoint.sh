#!/bin/sh
DATABASE_URI=postgresql://$DATABASE_USER:$DATABASE_PASSWORD@$DATABASE_HOST/$DATABASE_NAME
RETRIES=30

until psql $DATABASE_URI --command "select 1" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
  echo "Waiting for postgres server, $((RETRIES--)) remaining attempts…"
  sleep 1
done

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
