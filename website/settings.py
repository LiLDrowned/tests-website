import os

POSTGRES_PASSWORD = str(os.getenv('POSTGRES_PASSWORD') or 'root')
POSTGRES_USERNAME = str(os.getenv('POSTGRES_USER') or 'password')
POSTGRES_HOST = str(os.getenv('POSTGRES_HOST') or 'localhost')
POSTGRES_DATABASE = str(os.getenv('POSTGRES_DATABSE') or 'students_tests')

SECRET_KEY = str(os.getenv('SECRET_KEY') or 'chlebik s maslom')
