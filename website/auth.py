from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import conn, User
from flask_login import current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2.extras import DictCursor
from .groups import session

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated and request.method == 'GET':
        return redirect(url_for('groups.groups_menu'))

    if request.method == 'POST': # tuto staci elif, pretoze ak je predosla podmienka pravdiva, tak sa k tomuto kodu program ani nedostane

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

            else: # tuto ten else nie je potreba, pretoze ak bola predosla podmienka true, tak sa tento kod ani nevykona
                # password was incorrect
                flash('Incorrect password, try again.', category='error')
                # ak je nespravnny password, tak nema byt status code 200, ale 401
                # pozri si tieto linky
                # https://www.google.com/search?q=rest+status+code+table&client=firefox-b-d&source=lnms&tbm=isch&sa=X&ved=2ahUKEwi9q6bU39b8AhVpgP0HHT_FASwQ_AUoAXoECAEQAw&biw=1536&bih=739&dpr=1.25#imgrc=I6-YdSLC7R91BM
                # https://umbraco.com/knowledge-base/http-status-codes/
                # aby si vedel, ake status codes mas kedy vratit
                return render_template('login.html', user=current_user), 200

        # account is not in database
        else: # tento else tiez nie je potrebny, opat to iste co v predoslych pripadoch
            flash('Email does not exist.', category='error')
            # status code ma byt 401 a nie 200
            return render_template('login.html', user=current_user), 200

    else: # tento else tiez nie je potrebny
        return render_template('login.html', user=current_user), 200


@auth.route('/sign-up', methods=["POST", 'GET'])
def sign_up():

    if request.method == 'POST':

        # getting users input
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        # neda sa toto spravit trochu rozumnejsie, pretoze tolko podmienok za sebou vyzera dost zle...

        # checking if password is not too short
        if password != None and len(password) < 1:

            flash('Password is too short', category='error')
            # pridaj status code. Mozes pozriet, aky presne, ale urcite by to mala byt minimalne 400
            return render_template('sing_in.html', user=current_user)

        if email != None and len(email) < 1: # toto ma byt elif, nie nahodou?

            flash('Invalid e-mail', category='error')
            # pridaj status code. Mozes pozriet, aky presne, ale urcite by to mala byt minimalne 400
            return render_template('sing_in.html', user=current_user)

        if name != None and len(name) < 1: # toto ma byt elif, nie nahodou?

            flash('Your name is too short', category='error')
            # pridaj status code. Mozes pozriet, aky presne, ale urcite by to mala byt minimalne 400
            return render_template('sing_in.html', user=current_user)

        if confirm != None and len(confirm) < 1: # toto ma byt elif, nie nahodou?

            flash('Invalid password confirm', category='error')
            # pridaj status code. Mozes pozriet, aky presne, ale urcite by to mala byt minimalne 400
            return render_template('sing_in.html', user=current_user)


        else: # tento else nie je potrebny, pretoze ak platila niektora podmienka z predoslych, tak sa vykona return a tento kod dalej nepokracuje

            # checking if password match with confirming password
            if password == confirm:
                cur = conn.cursor(cursor_factory=DictCursor)
                cur.execute(f"SELECT * FROM users WHERE name ='{name}';")
                user = cur.fetchone()

                if not user:

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
                        # tu nemusis pouzivat (f'name', f'email', f'password') nie? A pravdepodobne by si ani nemal...
                        # staci (name, email, password, )
                        val = (f'{name}', f'{email}', f'{password1}', ) # toto by malo byt takto, aby si sa obranil proti SQL injection
                        # ohladom SQL injection pozri toto: https://www.w3schools.com/sql/sql_injection.asp
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

                    else: # tento else nie je potrebny

                        # account already exists on this email
                        flash('Account is already created on this email address.', category='error')
                        # zmenit status code minimalne 400, ale mohol by si pozriet, ktory presne
                        return render_template('sing_in.html', user=current_user), 200

                else: # tento else pravdepodobne tiez nie je potrebny
                    # password input invalid
                    flash("User name is already used.", category='error')
                    # zmenit status code minimalne 400, ale mohol by si pozriet, ktory presne
                    return render_template('sing_in.html', user=current_user), 200


            else: # zda sa mi, ze aj tento else nie je potrebny

                # password input invalid
                flash("Your password doesn't match.", category='error')
                # zmenit status code minimalne 400, ale mohol by si pozriet, ktory presne
                return render_template('sing_in.html', user=current_user), 200

    else: # tento else nie je potrebny

        return render_template('sing_in.html', user=current_user), 200


@auth.route('/logout', methods=["POST", "GET"])
def logout():
    # tieto zbytocne prints daj prec
    if 'group_id' in session:
        print(session.get('group_id'))
    # logging of user from users class
    session.clear()
    if 'group_id' in session:
        print(session.get('group_id'))
        print(session.get('admin'))

    logout_user()
    return redirect(url_for('auth.login'))
