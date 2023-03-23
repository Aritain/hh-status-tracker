FROM python:3.11.1-alpine3.17

COPY source/ /opt/hh_tracker

RUN pip3 install -r /opt/hh_tracker/requirements.txt

WORKDIR /opt/hh_tracker
ENTRYPOINT ["python3", "./main.py"]
