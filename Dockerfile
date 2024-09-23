# syntax=docker/dockerfile:1

FROM public.ecr.aws/docker/library/python:3.11.8-slim-bookworm

RUN apt-get update -y

WORKDIR /app
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

ENV FASTF1_CACHE="/cache"
CMD ["python3", "-u", "-m", "flask", "--app", "formula10", "run", "--host", "0.0.0.0"]
