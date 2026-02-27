# Purane version ki jagah 'bullseye' ya 'bookworm' use karein
FROM python:3.9-slim-bookworm

# Java install karne ki nayi command
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*;

# Flask dependencies
RUN pip install --no-cache-dir flask flask-cors gunicorn

WORKDIR /app
COPY . /app

# Render ke liye port 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "main:app"]
