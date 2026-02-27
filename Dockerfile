FROM python:3.9-slim-buster

# Java install karne ki command
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get clean;

# Flask dependencies
RUN pip install flask flask-cors gunicorn

WORKDIR /app
COPY . /app

# Render ke liye port 10000 zaruri hai
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "main:app"]
