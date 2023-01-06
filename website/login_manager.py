from flask_login import LoginManager
from .models import conn, User
from psycopg2.extras import DictCursor

login_manager = LoginManager()
# type: ignore -> Bug referring to None
login_manager.login_view = 'auth.login'  # type: ignore
login_manager.login_message_category = 'error'
login_manager.login_message = 'You need to login first to do this action.'


@login_manager.user_loader
def load_user(id):
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(f"SELECT * FROM users WHERE user_id = '{id}';")
    user = cur.fetchone()
    cur.close()

    return User(id) if user else None
