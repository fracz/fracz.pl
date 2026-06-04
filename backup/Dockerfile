FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       mariadb-client \
       rclone \
       gzip \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pyyaml

WORKDIR /app

COPY backup.py /app/backup.py

RUN chmod +x /app/backup.py

ENTRYPOINT ["python3", "/app/backup.py"]
