FROM python:3-slim

ENV PORT 8080
EXPOSE 8080
WORKDIR /usr/src/app

ADD flask /usr/src/app/flask
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app/flask
CMD [ "python", "./wsgi.py" ]
