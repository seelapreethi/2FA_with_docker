
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


FROM python:3.11-slim

ENV TZ=UTC

WORKDIR /app

RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone


COPY --from=builder /install /usr/local

COPY . .

COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron

RUN mkdir -p /data /cron && chmod 755 /data /cron

EXPOSE 8080

CMD cron && uvicorn app.main:app --host 0.0.0.0 --port 8080
