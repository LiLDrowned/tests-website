FROM python:3.9-alpine

WORKDIR /app

COPY ./requirements .

ENV PRODUCTION=production

RUN pip install -r requirements.txt

COPY . ./

EXPOSE 5000

CMD ["python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]