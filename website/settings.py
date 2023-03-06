import os

POSTGRES_PASSWORD = str(os.getenv('POSTGRES_PASSWORD') or 'rootpassword')
POSTGRES_USERNAME = str(os.getenv('POSTGRES_USER') or 'postgres')
POSTGRES_HOST = str(os.getenv('POSTGRES_HOST') or 'localhost')
POSTGRES_DATABASE = str(os.getenv('POSTGRES_DATABSE') or 'StudentsTests')

SECRET_KEY = str(os.getenv('SECRET_KEY') or 'chlebik s maslom')
