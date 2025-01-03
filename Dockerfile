FROM python:3.10-slim-bullseye

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

RUN pip install gunicorn

COPY . /app

CMD ["gunicorn", "-b", "0.0.0.0:42000", "--workers", "2", "main:app"]