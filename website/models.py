from .settings import DB_PASSWORD, DB_USERNAME
import psycopg2
from flask_login import UserMixin

conn = psycopg2.connect(
    host="localhost",
    database="StudentsTests",
    user=DB_USERNAME,
    password=DB_PASSWORD)

cur = conn.cursor()


cur.execute('CREATE TABLE IF NOT EXISTS users (user_id serial PRIMARY KEY,'
            'name varchar (255) NOT NULL, email varchar (255) NOT NULL, password varchar (255));')

cur.execute('CREATE TABLE IF NOT EXISTS groups (id serial PRIMARY KEY,'
            'group_name varchar (255) NOT NULL,group_id integer, user_id integer,group_admin varchar (255),'
            ' constraint fk_groups_users foreign key (user_id)'
            ' REFERENCES users (user_id));')

cur.execute('CREATE TABLE IF NOT EXISTS tests (test_id serial PRIMARY KEY,'
            'test_name varchar (255) NOT NULL, group_id integer NOT NULL,number_questions integer);')

cur.execute('CREATE TABLE IF NOT EXISTS questions (question_id serial PRIMARY KEY,'
            'question varchar (255) NOT NULL,asnwer1 varchar(255),asnwer2 varchar(255)'
            ',asnwer3 varchar(255),asnwer4 varchar(255),right_question varchar(255), test_id integer,'
            ' constraint fk_questions_tests foreign key (test_id)'
            ' REFERENCES tests (test_id), user_id integer, constraint fk_questions_users '
            ' foreign key (user_id) REFERENCES users (user_id) , question_number integer );')

cur.execute('CREATE TABLE IF NOT EXISTS invitations (invitation_id serial PRIMARY KEY,'
            'group_name varchar (255) NOT NULL,group_id integer,constraint fk_invitaions_groups foreign key (group_id)'
            ' REFERENCES groups (id),user_id integer, constraint fk_invitaions_users foreign key (user_id)'
            ' REFERENCES users (user_id));')

conn.commit()


class User(UserMixin):
    def __init__(self, id) -> None:
        super().__init__()
        self.id = id

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

