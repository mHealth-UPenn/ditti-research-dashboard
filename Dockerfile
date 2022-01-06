FROM python:slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y

RUN mkdir /log
ENV PYTHONUNBUFFERED=1
ENV FLASK_LOG_MOUNT=/log
ENV FLASK_APP=run.py

COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install wheel
RUN pip3 install -r requirements.txt

COPY . .
RUN rm requirements.txt

CMD python3 run.py
