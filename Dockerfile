FROM python:3

WORKDIR /home/
COPY requirements.txt /home/
RUN pip install -v -r requirements.txt
