FROM python:3.8-slim-buster
#FROM python:alpine

#RUN apt-get update && apt-get install -y python-dateutil
RUN pip install --no-cache-dir python-dateutil

ADD ftpclean.py .
ADD secrets.py .

CMD [ "python","./ftpclean.py"]