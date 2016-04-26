FROM iron/python:3

WORKDIR /home/
COPY requirements.txt /home/
RUN python3 -m ensurepip
RUN pip3 install -v -r requirements.txt
