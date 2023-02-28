from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import conn, User
from flask_login import current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2.extras import DictCursor
from .groups import session

auth = Blueprint('auth', __name__)


@auth.route('/login/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated and request.method == 'GET':
        return redirect(url_for('groups.groups_menu'))

    if request.method == 'POST':

        # getting data from user
        email = request.form.get('email')
        password = request.form.get('password')

        # looking if account exists in database
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute(f"SELECT * FROM users WHERE email ='{email}';")
        user = cur.fetchone()
        cur.close()
        # account was found
        if user:
            user_password = user['password']
            user_id = user['user_id']
            # looking if users passwords matchs
            if check_password_hash(user_password, password):

                # user was succesfully logged in
                # logining user in to models class
                logged_user = User(user_id)
                login_user(logged_user, remember=True)

                flash('Logged in successfully!', category='success')
                return redirect(url_for('groups.groups_menu'))

            else:
                # password was incorrect
                flash('Incorrect password, try again.', category='error')
                return render_template('login.html', user=current_user), 200

        # account is not in database
        else:
            flash('Email does not exist.', category='error')
            return render_template('login.html', user=current_user), 200

    else:
        return render_template('login.html', user=current_user), 200


@auth.route('/sign-up/', methods=["POST", 'GET'])
def sign_up():

    if request.method == 'POST':

        # getting users input
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        # checking if password is not too short
        if password != None and len(password) < 1:

            flash('Password is too short', category='error')
            return render_template('sing_in.html', user=current_user)

        if email != None and len(email) < 1:

            flash('Invalid e-mail', category='error')
            return render_template('sing_in.html', user=current_user)

        if name != None and len(name) < 1:

            flash('Your name is too short', category='error')
            return render_template('sing_in.html', user=current_user)

        if confirm != None and len(confirm) < 1:

            flash('Invalid password confirm', category='error')
            return render_template('sing_in.html', user=current_user)


        else:

            # checking if password match with confirming password
            if password == confirm:
                cur = conn.cursor(cursor_factory=DictCursor)
                cur.execute(f"SELECT * FROM users WHERE name ='{name}';")
                user = cur.fetchone()

                if  not user:

                    # looking if account exist with this email already exist
                    cur = conn.cursor(cursor_factory=DictCursor)
                    cur.execute(f"SELECT * FROM users WHERE email ='{email}';")
                    user = cur.fetchone()

                    # account is not found in database
                    if not user:

                        # hashing password
                        password1 = generate_password_hash(
                            password, method='sha256')

                        # adding user in to the database
                        sql = "INSERT INTO users (name, email,password) values (%s,%s,%s) RETURNING user_id;"
                        val = (f'{name}', f'{email}', f'{password1}')
                        cur.execute(sql, val)
                        conn.commit()

                        # getting users id
                        value_dict = cur.fetchone()
                        user_id = value_dict['user_id']
                        cur.close()

                        # logining user in to models class
                        user = User(str(user_id))
                        login_user(user, remember=True)

                        # user was succesfully logged in
                        flash('Logged in successfully!', category='success')
                        return redirect(url_for('groups.groups_menu'))

                    else:

                        # account already exists on this email
                        flash(
                            'Account is already created on this email address.', category='error')
                        return render_template('sing_in.html', user=current_user), 200

                else:
                    # password input invalid
                    flash("User name is already used.", category='error')
                    return render_template('sing_in.html', user=current_user), 200


            else:

                # password input invalid
                flash("Your password doesn't match.", category='error')
                return render_template('sing_in.html', user=current_user), 200

    else:

        return render_template('sing_in.html', user=current_user), 200


@auth.route('/logout/', methods=["POST", "GET"])
def logout():
    # logging of user from users class
    session.clear()

    flash("You have been successfully logged out!",category='success') 
    logout_user()
    
    return redirect(url_for('auth.login'))
