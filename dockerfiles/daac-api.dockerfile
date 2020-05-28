FROM registry.access.redhat.com/ubi8/python-36 

ENV PORT 8080
EXPOSE 8080
WORKDIR /usr/src/app

ADD flask /usr/src/app/flask
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app/flask
CMD [ "gunicorn", "main:app", "--bind=0.0.0.0:8080"]
