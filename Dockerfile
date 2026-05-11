# syntax=docker/dockerfile:1
FROM python:3.11
WORKDIR .
RUN apt-get update
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD gunicorn main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000 --threads 4 --workers 4 --timeout 900 --log-level 'debug'
