FROM python:3.6-alpine

RUN apk add --no-cache --update bash

RUN adduser -D kv_store

WORKDIR /home/kv_store

COPY app app
COPY kv_store.py config.py Pipfile Pipfile.lock ./

RUN pip install pipenv
RUN pipenv install --system

RUN chown -R kv_store:kv_store ./
USER kv_store

EXPOSE 5000
CMD gunicorn -b :5000 --access-logfile - --error-logfile - kv_store:app
