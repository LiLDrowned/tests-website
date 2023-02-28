from website import create_app
from flask import redirect, url_for
import time

# not a clever way to wait for db
# in future maybe replace with this https://stackoverflow.com/questions/35069027/docker-wait-for-postgresql-to-be-running
time.sleep(20) 

app = create_app()


@app.route('/') 
def re_routing():
    return redirect(url_for('auth.login'))


if __name__ == '__main__':
    app.run(debug=True)
