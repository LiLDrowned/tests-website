from flask import Flask
from .settings import SECRET_KEY


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY

    from website.login_manager import login_manager
    login_manager.init_app(app)

    from .groups import groups
    from .auth import auth
    from .tests import tests

    app.register_blueprint(groups, url_prefix='/groups')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(tests, url_prefix='/tests')

    return app
