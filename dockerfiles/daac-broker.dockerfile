FROM registry.redhat.io/ubi8/python-36
ENV PORT 8080
EXPOSE 8080
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY flask/* .

ENTRYPOINT ["python"] 
CMD ["wsgi.py"]