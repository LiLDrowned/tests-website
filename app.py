from website import create_app
from flask import redirect, url_for

app = create_app()


@app.route('/') 
def re_routing():
    return redirect(url_for('auth.login'))


if __name__ == '__main__':
    app.run(debug=True)
