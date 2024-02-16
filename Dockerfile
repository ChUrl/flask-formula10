# syntax=docker/dockerfile:1

FROM python:3.10.1-slim-buster
RUN apt-get update -y
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python3", "-u", "formula10.py"]
