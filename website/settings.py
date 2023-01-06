import os

DB_PASSWORD = str(os.getenv('DB_PASSWORD') or 'rootpassword')
DB_USERNAME = str(os.getenv('DB_USERNAME') or 'postgres')
SECRET_KEY = str(os.getenv('SECRET_KEY') or 'chlebik s maslom')
