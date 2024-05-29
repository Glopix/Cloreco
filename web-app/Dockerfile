FROM python:3.12 as base
RUN pip install flask flask_sse flask-wtf celery configparser pandas docker loguru plotnine ansi2html

ADD app /app
ADD data /app/data_default

ENV CELERY_BROKER_URL=redis://redis
ENV CELERY_RESULT_BACKEND=redis://redis
ENV FLASK_REDIS_URL=redis://redis:6379

ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app

LABEL org.opencontainers.image.source https://github.com/Glopix/Cloreco


# frontend image, used to run the gunicorn webserver and flask
FROM base as frontend
RUN pip install gunicorn gevent
ENV FLASK_APP=run.py
#ENTRYPOINT [ "flask", "run", "-h", "0.0.0.0"]
ENTRYPOINT [ "gunicorn", "run:app", "--worker-class", "gevent", "--bind", "0.0.0.0:5000" ]


# backend image, used to run celery and start the docker containers
FROM base as backend
ENV CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP=True
ENTRYPOINT [ "celery", "-A", "run.celery", "worker", "--loglevel=info" ]
