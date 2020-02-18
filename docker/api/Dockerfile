FROM python:3.8-alpine
WORKDIR /usr/src/app

# Install Alpine packages
RUN apk update && apk add gcc musl-dev postgresql-client postgresql-dev

# Install Python packages
COPY docker/api/requirements.lock .
RUN pip install --upgrade pip
RUN pip install --requirement requirements.lock

# Add application code
COPY src/app app
RUN rm app/settings.py
COPY src/manage.py .

# Add entrypoint script
COPY docker/api/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 8000
CMD []
