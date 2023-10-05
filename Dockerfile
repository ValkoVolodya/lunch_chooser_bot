FROM python:3.11.3-slim-bullseye

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

CMD python lunch_chooser_bot.py
