FROM python:3-alpine

COPY passwd elmer_client.py requirements.txt /usr/local/bin/

RUN pip install -r /usr/local/bin/requirements.txt

WORKDIR /data

ENTRYPOINT ["/bin/sh"]
