import os

DB_PASSWORD = str(os.getenv('POSTGRES_PASSWORD') or 'rootpassword')
DB_USERNAME = str(os.getenv('POSTGRES_USER') or 'postgres')
SECRET_KEY = str(os.getenv('SECRET_KEY') or 'chlebik s maslom')
