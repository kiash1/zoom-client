FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app /app/app
COPY ./scripts/init.sh /app/init.sh
ENTRYPOINT ["/bin/bash", "/app/init.sh"]
EXPOSE 5000
