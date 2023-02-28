FROM python:3.9-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . ./

EXPOSE 5000

CMD ["python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]