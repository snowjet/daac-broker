FROM python:3-slim

ENV PORT 8080
EXPOSE 8080
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY flask/* /usr/src/app

ENTRYPOINT ["python"] 
CMD ["wsgi.py"]