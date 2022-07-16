FROM python:3.10 AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY ./req.txt .
RUN pip install -r req.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r req.txt


FROM python:3.10

RUN mkdir -p /home/app

RUN adduser --system --group hdhbot \
    && usermod -aG www-data hdhbot \
    && usermod -aG sudo hdhbot

ENV HOME=/home/app
ENV APP_HOME=/home/app/bot
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/req.txt .
RUN pip install --no-cache /wheels/*

COPY . $APP_HOME

RUN chown -R hdhbot:hdhbot $APP_HOME

USER hdhbot
