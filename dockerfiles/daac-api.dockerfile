FROM registry.access.redhat.com/ubi8/python-36 


ENV PROJECT_NAME='DCaaS API Broker'

# Change the default GUACADMIn_PASSWORD
ENV GUACADMIN_PASSWORD=''

# Route to GUAC
ENV GUAC_URL=''
# Project / Namespace name in OpenShift
ENV NAMESPACE=''

# Postgres
ENV POSTGRES_HOST=127.0.0.1 \
    POSTGRES_PORT=5432 \
    POSTGRES_USER=guac \
    POSTGRES_PASSWORD=guac_pass \
    POSTGRES_DB=guacamole_db 

ENV SECRET_KEY='SOME SECRET VALUE'
ENV LOG_LEVEL='DEBUG'

ENV PORT 8080
EXPOSE 8080
WORKDIR /usr/src/app

ADD flask /usr/src/app/flask
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app/flask
CMD [ "gunicorn", "main:app", "--bind=0.0.0.0:8080"]
