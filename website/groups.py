from flask import Blueprint, render_template, request,session, redirect, url_for,flash
from .models import conn
from flask_login import current_user, login_required
from psycopg2.extras import DictCursor

groups = Blueprint('groups', __name__)

@groups.route('/groups-menu/',methods = ["POST","GET"])
@login_required
def groups_menu():

    cur = conn.cursor(cursor_factory=DictCursor)
    user_id = current_user.id

    cur.execute(f"SELECT * FROM invitations WHERE user_id ={user_id}")
    invitations = cur.fetchall()

    cur.execute(f"SELECT * FROM groups WHERE user_id = {user_id}")
    groups = cur.fetchall()

    cur.close()
    return render_template('groups_menu.html',invitations = invitations,user = current_user,
                            groups = groups,page = 'Home')

@groups.route('/group/<group_id>/',methods = ["GET"])
@login_required
def group(group_id):

    if 'group_id' in session:   
        session.pop('group_id')
        if 'admin' in session:
            session.pop('admin')
            if 'test_id' in session:
                session.pop('test_id')

    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM users WHERE user_id IN"
                f"(SELECT user_id FROM groups WHERE group_id = {group_id});")
    members = cur.fetchall()

    cur.execute(f"SELECT * FROM users WHERE user_id IN (SELECT user_id FROM invitations WHERE group_id ={group_id});")
    invites = cur.fetchall()

    user_id = current_user.id

    cur.execute(f"SELECT * FROM groups WHERE group_id = {group_id} AND user_id = {user_id}")
    value = cur.fetchone()
    cur.close()

    if value != None:

        session['group_id'] = group_id
        group_id = session['group_id']

        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute(f"SELECT group_name,group_admin FROM groups WHERE group_id = {group_id} AND"
                    f" user_id = {user_id};")
        
        users_group = cur.fetchone()

        cur.execute(f"SELECT test_id,test_name FROM tests WHERE group_id = {group_id};")
        tests = cur.fetchall()

        cur.close()

        if users_group['group_admin'] != None:
            
            session['admin'] = True
            admin = session.get('admin')

        else:
            admin = False

        
        return render_template('current_group.html',user = current_user,
            group_name = users_group['group_name'],members = members,tests = tests,page = 'Group'
            ,group_id = group_id,admin = admin,invites = invites)

    else:

        flash('You are not a member of this group!', category='error')
        return redirect(url_for('groups.groups_menu'))

@groups.route('/create-group/',methods = ["POST","GET"])
@login_required
def create_group():

    if request.method == 'POST':

        group_name = request.form.get('group_name')
        
        if group_name == '':
            flash('Enter name for the group!', category='error')
            return redirect(url_for('groups.create_group'))

        user_id = current_user.id

        cur = conn.cursor(cursor_factory=DictCursor)

        sql = "INSERT INTO groups(group_name,user_id,group_admin) values (%s,%s,%s) RETURNING id"
        values = (f'{group_name}',user_id,'True')

        cur.execute(sql,values)
        conn.commit()

        group_id = cur.fetchone()['id']

        cur.execute(f"UPDATE groups SET group_id = {group_id} WHERE id = {group_id};")
        conn.commit()

        cur.close()

        flash('Group has been created!', category='success')
        return redirect(url_for('groups.groups_menu'))

    return render_template('create_group.html',user = current_user)

@groups.route('/people/',methods = ["POST","GET"])
@login_required
def people():

    if 'group_id' in session:
        group_id = session.get('group_id')

        if request.method == "POST":

            search = request.form.get('search')

            if search != None :

                
                cur = conn.cursor(cursor_factory=DictCursor)
                cur.execute(f"SELECT * FROM users WHERE LOWER(name) LIKE LOWER('{search}%')"
                        f" AND user_id NOT IN (SELECT user_id FROM groups WHERE group_id = {group_id})"
                        f" AND user_id NOT IN (SELECT user_id FROM invitations WHERE group_id = {group_id})")

                finds = cur.fetchall()
                cur.close()

                return render_template('people.html',user = current_user,people = finds ,page = 'Group',
                                    group_id = group_id)

            else:
                flash('Enter characters!', category='error')
                return redirect(url_for('groups.people'))

        else:

            cur = conn.cursor()
        
            cur.execute("SELECT * FROM users WHERE user_id NOT IN(SELECT user_id FROM "
                        f"groups WHERE group_id = {group_id}) AND user_id NOT IN"
                        f"(SELECT user_id FROM invitations WHERE group_id = {group_id})")
                
            people = cur.fetchall()
            cur.close()

            return render_template('people.html',user = current_user,people = people ,page = 'Group',
                                    group_id = group_id)
        
                
    else:
        flash('You are not member of this group!', category='error')
        return redirect(url_for('groups.groups_menu'))

@groups.route('/kick-person/<int:user_id>/', methods = ["GET","DELETE"])
@login_required
def kick_person(user_id):
    if 'group_id' in session:

        group_id = session.get('group_id')

        if 'admin' in session:
            
            cur = conn.cursor(cursor_factory=DictCursor)

            cur.execute(f"DELETE FROM invitations WHERE group_id = {group_id} AND user_id = {user_id};")
            conn.commit()

            cur.execute(f"DELETE FROM groups WHERE group_id = {group_id} AND user_id = {user_id};")
            conn.commit()

            cur.close()

            flash('User has been kicked from group!', category='success')
            return redirect(url_for('groups.group',group_id = group_id))

        else:
            flash("You don't have permision to do this action!" ,category='error')
            return redirect(url_for('groups.group',group_id = group_id))

    else:

        flash('You are not member of the group!', category='error')
        return redirect(url_for('groups.groups_menu')) 

@groups.route('/leave-group/<int:user_id>/', methods = ["GET","DELETE"])
@login_required
def leave_group(user_id):
    if 'group_id' in session:
        group_id = session.get('group_id')

        cur = conn.cursor(cursor_factory=DictCursor)

        cur.execute(f"SELECT * FROM groups WHERE group_id = {group_id} AND user_id = {user_id};")
        user = cur.fetchone()

        if user['group_admin'] == 'True':
            cur.execute(f"SELECT * FROM groups WHERE group_id = {group_id};")
            all_users = cur.fetchall()

            if len(all_users) == 1:
                cur.execute(f"DELETE FROM invitations WHERE group_id = {group_id};")

                cur.execute(f"DELETE FROM questions WHERE group_id = {group_id}")

                cur.execute(f"DELETE FROM tests WHERE group_id = {group_id}")

                cur.execute(f"DELETE FROM groups WHERE user_id = {user_id} AND group_id = {group_id};")

                conn.commit()
                cur.close()

                flash('You have left the group!', category='success')
                return redirect(url_for('groups.groups_menu'))
            
            else:
                cur.execute(f"DELETE FROM groups WHERE user_id = {user_id} AND group_id = {group_id};")
                
                cur.execute(f"SELECT * FROM groups WHERE group_id = {group_id};")
                users = cur.fetchone()['user_id']

                cur.execute("UPDATE groups SET group_admin = 'True' "
                           f" WHERE group_id = {group_id} AND user_id = {users}")

                conn.commit()
                cur.close()

                flash('You have left the group!', category='success')
                return redirect(url_for('groups.groups_menu'))
        else:
            cur.execute(f"DELETE FROM groups WHERE user_id = {user_id} AND group_id = {group_id};")
            
            conn.commit()
            cur.close()

            flash('You have left the group!', category='success')
            return redirect(url_for('groups.groups_menu'))

    else:

        flash('You are not member of the group!', category='error')
        return redirect(url_for('groups.groups_menu')) 

@groups.route('/deleting-group/<int:group_id>/', methods = ["GET","DELETE"])
@login_required
def delete_group(group_id):
    
        user_id = current_user.id
        group_id = session.get('group_id')

        cur = conn.cursor(cursor_factory=DictCursor)

        cur.execute(f"SELECT * FROM groups WHERE group_id = {group_id} AND user_id = {user_id};")
        user = cur.fetchone()

        if user['group_admin'] == 'True':
            cur.execute(f"SELECT * FROM groups WHERE group_id = {group_id};")
            all_users = cur.fetchall()

            if len(all_users) == 1:
                cur.execute(f"DELETE FROM invitations WHERE group_id = {group_id};")

                cur.execute(f"DELETE FROM questions WHERE group_id = {group_id};")

                cur.execute(f"DELETE FROM tests WHERE group_id = {group_id};")

                cur.execute(f"DELETE FROM groups WHERE user_id = {user_id} AND group_id = {group_id};")

                conn.commit()
                cur.close()

                flash('You have left the group!', category='success')
                return redirect(url_for('groups.groups_menu'))
            
            else:
                cur.execute(f"DELETE FROM groups WHERE user_id = {user_id} AND group_id = {group_id};")
                
                cur.execute(f"SELECT * FROM groups WHERE group_id = {group_id};")
                users = cur.fetchone()['user_id']

                cur.execute("UPDATE groups SET group_admin = 'True' "
                           f" WHERE group_id = {group_id} AND user_id = {users};")

                conn.commit()
                cur.close()

                flash('You have left the group!', category='success')
                return redirect(url_for('groups.groups_menu'))
        else:
            cur.execute(f"DELETE FROM groups WHERE user_id = {user_id} AND group_id = {group_id};")
            
            conn.commit()
            cur.close()

            flash('You have left the group!', category='success')
            return redirect(url_for('groups.groups_menu'))


@groups.route('/add-person/<int:user_id>/', methods = ["GET", "PUT"])
@login_required
def add_person(user_id):

    group_id = session.get('group_id')
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute(f"SELECT group_name FROM groups WHERE group_id={group_id};")
    group = cur.fetchone()
    group_name = group['group_name']

    sql = "INSERT INTO invitations (group_name, group_id, user_id) values (%s,%s,%s);"
    val = (f'{group_name}', group_id, user_id)
    cur.execute(sql,val)

    conn.commit()
    cur.close()
    
    flash('User has been invited!', category='success')
    return redirect(url_for('groups.people'))

@groups.route('/join-group/<group_id>/<group_name>/',methods = ["GET","PUT"])
@login_required
def join_group(group_id,group_name):
    
    cur = conn.cursor(cursor_factory=DictCursor)
    user_id = current_user.id
    cur.execute(f"DELETE FROM invitations WHERE user_id = {user_id} AND group_id = {group_id};")

    postsql = "INSERT INTO groups(group_id,group_name,user_id) values (%s,%s,%s)"
    val = (group_id,f'{group_name}', user_id)

    cur.execute(postsql,val)
    conn.commit()
    cur.close()

    flash('You have been added to the group!',category='success' )
    return redirect(url_for('groups.groups_menu'))

@groups.route('/cancel-invite/<int:group_id>/',methods = ["GET","PUT"])
@login_required
def cancel_invite(group_id):
    user_id = current_user.id

    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(f"DELETE FROM invitations WHERE user_id = {user_id} AND group_id = {group_id};")

    conn.commit()
    cur.close()

    flash('Group invitation has been declined!',category='success')
    return redirect(url_for('groups.groups_menu'))