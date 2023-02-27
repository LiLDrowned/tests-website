from flask import Blueprint, render_template, request, redirect, url_for,flash
from .models import conn
from flask_login import current_user, login_required
from psycopg2.extras import DictCursor
from .groups import session

tests = Blueprint('tests', __name__)

@tests.route('/create-test/',methods = ["POST","GET"])
@login_required
def create_test():
    if 'group_id' in session:

        group_id = session.get('group_id')

        if 'admin' in session:
            admin = session.get('admin')
        else:
            admin = False

        if 'test_id' in session:
            session.pop('test_id')


        if request.method == 'POST':

            global questions
            questions = {}

            test_name = request.form.get('test_name')

            session['test_name'] = test_name
            session['max_question'] = 1
            
            flash('Test name has been saved!',category='success')
            return redirect(url_for('tests.create_questions',current_question = 1))

        else:

            return render_template('create_test.html',user = current_user,page = 'Group'
                                   ,group_id = group_id,admin = admin)
    
    else:
        flash("You are not memebr of the group!",category='error') 
        return redirect(url_for('groups.groups_menu'))

@tests.route('/create-questions/<int:current_question>/',methods = ["POST","GET"])
@login_required
def create_questions(current_question):

    if 'group_id' in session:
        group_id = session.get('group_id')

        if 'admin' in session:
            admin = session.get('admin')

        else:
            admin = False

        if request.method == 'POST':
            print(request.form['action-btn'])
            
            if request.form['action-btn'] == 'Delete':
                return delete_question(current_question)
            
            elif request.form['action-btn'] == 'Add':
                return add_question(current_question)

            elif request.form['action-btn'] == 'Done':
                return save_question(current_question,'Complete')
            
            elif request.form['action-btn'] == '<<':
                return save_question(current_question,current_question -1)

            elif request.form['action-btn'] == '>>':
                return save_question(current_question,current_question + 1)
            
            else:
                number = request.form.get('action-btn')
                return save_question(current_question,number)

        else:
            max_question = session.get('max_question')
            return render_template('question_create.html',user = current_user,page = 'Group',admin = admin,
                                group_id = group_id,current_question = current_question
                                ,max_question = max_question,questions = questions)

    else:
        flash("You are not memebr of the group!",category='error') 
        return redirect(url_for('groups.groups_menu'))

@tests.route('/sessions-edit-test/<int:test_id>/')
@login_required
def sessions_edit_test(test_id):
    global questions
    questions = {}
    user_id = current_user.id

    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute(f"SELECT * FROM questions WHERE user_id = '{user_id}' AND test_id = '{test_id}';")
    users_questions = cur.fetchall()

    cur.close()

    question_number = 1
    for question in users_questions:
        questions[question_number] = {}
        questions[question_number]['question'] = question['question']
        questions[question_number]['answer1'] = question['asnwer1']
        questions[question_number]['answer2'] = question['asnwer2']
        questions[question_number]['answer3'] = question['asnwer3']
        questions[question_number]['answer4'] = question['asnwer4']
        questions[question_number]['right_answer'] = question['right_question']
        question_number += 1

    if question_number != 1:
        session['max_question'] = question_number -1 

    else:
        session['max_question'] = 1


    session['test_id'] = test_id
    
    return redirect(url_for('tests.edit_test',current_question = 1))


@tests.route('/edit-test/<int:current_question>/',methods = ["POST","GET"])
@login_required
def edit_test(current_question): 

    if 'group_id' in session:
        group_id = session.get('group_id')

        if 'admin' in session:
            admin = session.get('admin')

        else:
            admin = False

        if request.method == 'POST':
            if request.form['action-btn'] == 'Delete':
                return delete_question(str(current_question))
            
            elif request.form['action-btn'] == 'Add':
                return add_question(str(current_question))

            elif request.form['action-btn'] == 'Done':
                return save_question(current_question,'Update')
            
            elif request.form['action-btn'] == '<<':
                return save_question(current_question,str(current_question -1))

            elif request.form['action-btn'] == '>>':
                return save_question(current_question,str(current_question + 1))
            
            else:
                number = request.form.get('action-btn')
                return save_question(current_question,str(number))
            
        else:
            max_question = session.get('max_question')

            return render_template('edit_test.html',user = current_user,page = 'Group',admin = admin,
                            group_id = group_id,questions = questions,current_question = current_question,
                            max_question = max_question)

    else:
        flash("You are not memebr of the group!",category='error') 
        return redirect(url_for('groups.groups_menu'))

@tests.route('/sessions-start-test/<int:test_id>/',methods = ["POST","GET"])
@login_required
def session_start_test(test_id):
    global answers
    answers = {}

    session['test_id'] = test_id

    return redirect(url_for('tests.start_test',current_question = 1))

@tests.route('/start-test/<int:current_question>/',methods = ["POST","GET"])
@login_required
def start_test(current_question): 
    global answers

    if 'group_id' in session:
        group_id = session.get('group_id')

        if 'admin' in session:
            admin = session.get('admin')

        else:
            admin = False


        if request.method == 'POST':
        
            if request.form['action-btn'] == 'Done':
                return save_answer(current_question,'results')
            
            elif request.form['action-btn'] == '<<':
                return save_answer(current_question,current_question - 1)

            elif request.form['action-btn'] == '>>':
                return save_answer(current_question,current_question + 1)
            
            else:
                number = request.form.get('action-btn')
                return save_answer(current_question,number)

        else:

            test_id = session.get('test_id')
            cur = conn.cursor(cursor_factory=DictCursor)

            cur.execute(f"SELECT * FROM questions WHERE test_id = '{test_id}'")
            questions = cur.fetchall()

            cur.execute(f"SELECT * FROM tests WHERE test_id = '{test_id}'")
            test = cur.fetchone()

            cur.close()

            return render_template('start_test.html',user = current_user,page = 'Group',admin = admin,
                        group_id = group_id,current_question = current_question
                        ,questions = questions,max_question = test['number_questions'],answers = answers)

    else:
        flash("You are not memebr of the group!",category='error') 
        return redirect(url_for('groups.groups_menu'))

@tests.route('/test_results/<int:current_question>/',methods = ["GET"])
@login_required
def test_results(current_question):

    if 'group_id' in session and 'test_id' in session:

        group_id = session.get('group_id')
        test_id = session.get('test_id')

        if 'admin' in session:
            admin = session.get('admin')

        else:
            admin = False
            

        cur = conn.cursor(cursor_factory=DictCursor)

        cur.execute(f"SELECT right_question FROM questions WHERE test_id = '{test_id}';")
        right_answers = cur.fetchall()

        cur.execute(f"SELECT * FROM questions WHERE test_id = '{test_id}'")
        questions = cur.fetchall()

        cur.close()

        number_questions = 0
        for ele in right_answers:
            number_questions += 1


        points = 0
        all_answers = {}

        for ele in range(1,number_questions + 1):
            if right_answers[ele - 1]['right_question'] == answers[ele]:
                all_answers[ele] = answers[ele]
                points += 1
            else:
                all_answers[ele] = answers[ele]
        
        percentage = round((points / number_questions) * 100,2)

        return render_template('test_results.html',right_answers = right_answers,user_answers = answers,
            percentage = percentage,max_question = number_questions,points = points,questions = questions
            ,user = current_user,page = 'Group',admin = admin,group_id = group_id
            ,current_question=current_question,all_answers = all_answers)

    
    else:
        flash("You are not memebr of the group!",category='error') 
        return redirect(url_for('groups.groups_menu'))

@tests.route('/sessions-delete-questions/<test_id>/',methods = ["POST","GET"])
@login_required
def session_delete_question(test_id): 
    if 'group_id' in session:
        
        if 'admin' in session:

            cur = conn.cursor(cursor_factory=DictCursor)

            cur.execute(f"SELECT * FROM tests WHERE test_id = '{test_id}'")
            number_questions = cur.fetchone()

            cur.close()

            session['test_id'] = test_id
            session['max_question'] = number_questions['number_questions']

            return redirect(url_for('tests.delete_questions',current_question = 1))

        else:
            flash("You don't have permision to do this!",category='error') 
            return redirect(url_for('groups.groups_menu'))

    else:
        flash("You are not memebr of the group!",category='error') 
        return redirect(url_for('groups.groups_menu'))

@tests.route('/delete-questions/<int:current_question>/',methods = ["GET"])
@login_required
def delete_questions(current_question): 
    if 'group_id' in session:

        if 'admin' in session:

            group_id = session.get('group_id')
            admin = session.get('admin')
            max_question = session.get('max_question')
            test_id = session.get('test_id')

            cur = conn.cursor(cursor_factory=DictCursor)
            
            cur.execute(f"SELECT * FROM questions WHERE test_id = '{test_id}';")
            questions = cur.fetchall()

            cur.close()

            return render_template('delete-questions.html',user = current_user,page = 'Group',admin = admin,
                            group_id = group_id,questions = questions,current_question = current_question,
                            max_question = max_question)
        else:
            flash("You don't have permision to do this!",category='error') 
            return redirect(url_for('groups.groups_menu'))

    else:
        flash("You are not memebr of the group!",category='error') 
        return redirect(url_for('groups.groups_menu'))

@tests.route('/actions-delete-questions/<int:current_question>/<action>/<int:question_id>/'
                ,methods = ["DELETE","GET"])
@login_required
def actions_delete_questions(current_question,action,question_id):
    if 'group_id' in session:
        group_id = session.get('group_id')

        if 'admin' in session:
            max_question = session.get('max_question')
            test_id = session.get('test_id')

            if action == 'Delete':
                
                max_question -= 1
                session['max_question'] = max_question
                print(max_question)

                cur = conn.cursor(cursor_factory=DictCursor)

                cur.execute(f"DELETE FROM questions WHERE question_id = '{question_id}';")

                if max_question == 0 :

                    cur.execute(f"DELETE FROM tests WHERE test_id = '{test_id}'")
                    

                    conn.commit()
                    cur.close()

                    flash('Test has been deleted!',category='success')
                    return redirect(url_for('groups.group',group_id = group_id))
                
                cur.execute(f"UPDATE tests SET number_questions = '{max_question}' WHERE test_id = '{test_id}';")

                conn.commit()
                cur.close()

                flash(f'Question {current_question} has been deleted!',category='success')

                if current_question != 1 and max_question < current_question:
                    return redirect(url_for('tests.delete_questions',current_question = current_question - 1))

                else:
                    return redirect(url_for('tests.delete_questions',current_question = current_question))


            elif action == 'Delete Test':

                cur = conn.cursor(cursor_factory=DictCursor)
                
                cur.execute(f"DELETE FROM questions WHERE test_id = '{test_id}'")

                cur.execute(f"DELETE FROM tests WHERE test_id = '{test_id}'")

                conn.commit()
                cur.close()

                flash('Test has been deleted!',category='success')
                return redirect(url_for('groups.group',group_id = group_id))

        else:
            flash("You don't have permision for this!",category='error')    
            return redirect(url_for('groups.groups_menu'))

    else:
        flash("You are not memeber of the group!",category='error') 
        return redirect(url_for('groups.groups_menu'))

   
###### Creatting new test with questions #####

# adding question 
def add_question(current_question):

    max_question = session.get('max_question')
    
    session['max_question'] = max_question + 1

    if isinstance(current_question,int):
        return save_question(current_question,max_question + 1)
    
    else:
        return save_question(int(current_question),str(max_question + 1))

# saving question
def save_question(current_question,next_question):
    global questions

    if current_question not in questions:
        questions[current_question] = {}

    question = request.form.get('question')

    answer1 = request.form.get('answer1')
    answer2 = request.form.get('answer2')
    answer3 = request.form.get('answer3')
    answer4 = request.form.get('answer4')

    right_answer = request.form.get('right_answer')
    answers_val = [question,answer1,answer2,answer3,answer4]
    answers_str = ['question','answer1','answer2','answer3','answer4','right_answer']

    for numbers in range(0,4):
        if f'a{numbers + 1}' == right_answer:
            answers_val.append(f'a{numbers + 1}')

    for number in range(0,6):
        
        if answers_val[number] != '':
            try:
                del questions[current_question][answers_str[number]]
                questions[current_question][answers_str[number]] = answers_val[number]
            except:
                questions[current_question][answers_str[number]] = answers_val[number]

    if next_question == 'Complete':
        return complete_test()

    elif next_question == 'Update':
        return update_test()
    
    if isinstance(next_question,int):
        return redirect(url_for('tests.create_questions',current_question = next_question))

    else:
        return redirect(url_for('tests.edit_test',current_question = int(next_question)))

# deleting question 
def delete_question(current_question):
    global questions
    
    max_question = session.get('max_question')
    # its deleting the last question not the current question
    if int(current_question) in questions:
    
        questions_change = []

        questions.pop(int(current_question))

        for question in questions:
            print('question',question)
            if question > int(current_question):
                questions_change.append(question)
        
        for number in questions_change:
            questions[number - 1] = questions.pop(number)

        
    if max_question > 1 :
        
        max_question -= 1

        session['max_question'] = max_question

        print('delete',questions,'max questions:', max_question)

    flash(f'Question {int(current_question)} has been deleted!',category='success')

    if isinstance(current_question,int):

        if current_question != 1 and max_question < current_question:
            return redirect(url_for('tests.create_questions',current_question = current_question - 1))

        else:
            return redirect(url_for('tests.create_questions',current_question = current_question ))
    
    else:
        if int(current_question) != 1 and max_question < int(current_question):
            return redirect(url_for('tests.edit_test',current_question = int(current_question) - 1))

        else:
            return redirect(url_for('tests.edit_test',current_question = int(current_question) ))

# completing test
def complete_test():
    global questions

    test_name = session.get('test_name')
    group_id = session.get('group_id')
    max_question = session.get('max_question')
    user_id = current_user.id

    del session['test_name']
    del session['max_question']

    if max_question == 1 and len(questions[1]) == 1:
        
        return redirect(url_for('groups.group',group_id = group_id))


    cur = conn.cursor(cursor_factory=DictCursor)

    sql = "INSERT INTO tests(test_name,group_id,number_questions) values(%s,%s,%s) RETURNING test_id"
    val = (f'{test_name}',f'{group_id}',f'{max_question}')
    cur.execute(sql,val)


    value_dict = cur.fetchone()
    test_id = value_dict['test_id']

    str_val = ('question','answer1','answer2','answer3','answer4','right_answer')

    for question in questions:
        
        if str_val[0] not in questions[question]:
            questions[question][str_val[0]] = ''
        
        if str_val[1] not in questions[question]:
            questions[question][str_val[1]] = ''

        if str_val[2] not in questions[question]:
            questions[question][str_val[2]] = ''

        if str_val[3] not in questions[question]:
            questions[question][str_val[3]] = ''
    
        if str_val[4] not in questions[question]:
            questions[question][str_val[4]] = ''

        if str_val[5] not in questions[question]:
            questions[question][str_val[5]] = ''

        sql = "INSERT INTO questions(question,asnwer1,asnwer2,asnwer3,asnwer4,right_question,test_id,user_id,group_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        val = (f'{questions[question][str_val[0]]}',f'{questions[question][str_val[1]]}'
        ,f'{questions[question][str_val[2]]}',f'{questions[question][str_val[3]]}'
        ,f'{questions[question][str_val[4]]}',f'{questions[question][str_val[5]]}',f'{test_id}'
        ,f'{user_id}',f'{group_id}')
        

        cur.execute(sql,val)
        conn.commit()
    
    cur.close() 
    questions.clear()

    flash('Test has been created!',category='success')

    return redirect(url_for('groups.group',group_id = group_id))
#####

##### Doing test #####
def save_answer(current_question,next_question):
    global answers
    test_id = session.get('test_id')

    if current_question not in answers:
        answers[current_question] = {}
    
    users_answer = request.form.get('answers_options')
    
    if users_answer != None:
        answers[current_question] = users_answer

    if next_question == 'results':
        return redirect(url_for('tests.test_results', current_question = 1))

    return redirect(url_for('tests.start_test',current_question = next_question))
#####

##### Editting test #####
def update_test():
    user_id = current_user.id

    test_id = session.get('test_id')
    group_id = session.get('group_id')
    max_question = session.get('max_question')

    del session['test_id']
    del session['max_question']

    print(questions)
    print(len(questions))

    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute(f"SELECT * FROM questions WHERE test_id = '{test_id}' AND user_id != '{user_id}';")
    number_questions = cur.fetchall()

    if max_question == 1 and len(questions[1]) == 1 :
        
        cur.execute(f"DELETE FROM questions WHERE user_id = '{user_id}' AND test_id = '{test_id}'")
        

        if len(number_questions) == 0 :
            cur.execute(f"DELETE FROM tests WHERE test_id = '{test_id}'")

        else:
            cur.execute(f"UPDATE tests SET number_questions = '{len(number_questions)}' WHERE test_id = '{test_id}';")

        conn.commit()
        cur.close()

        return redirect(url_for('groups.group',group_id = group_id))

    print('questions number :',len(number_questions) + max_question )
    all_questions = len(number_questions) + max_question

    cur.execute(f"UPDATE tests SET number_questions = '{all_questions}' WHERE test_id = '{test_id}';")

    cur.execute(f"DELETE FROM questions WHERE user_id = '{user_id}' AND test_id = '{test_id}';")

    conn.commit()

    str_val = ('question','answer1','answer2','answer3','answer4','right_answer')

    for question in questions:
        if str_val[0] not in questions[question]:
            questions[question][str_val[0]] = ''
        
        if str_val[1] not in questions[question]:
            questions[question][str_val[1]] = ''

        if str_val[2] not in questions[question]:
            questions[question][str_val[2]] = ''

        if str_val[3] not in questions[question]:
            questions[question][str_val[3]] = ''
    
        if str_val[4] not in questions[question]:
            questions[question][str_val[4]] = ''

        if str_val[5] not in questions[question]:
            questions[question][str_val[5]] = ''

        sql = "INSERT INTO questions(question,asnwer1,asnwer2,asnwer3,asnwer4,right_question,test_id,user_id,group_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        val = (f'{questions[question][str_val[0]]}',f'{questions[question][str_val[1]]}'
        ,f'{questions[question][str_val[2]]}',f'{questions[question][str_val[3]]}'
        ,f'{questions[question][str_val[4]]}',f'{questions[question][str_val[5]]}',f'{test_id}'
        ,f'{user_id}',f'{group_id}')

        cur.execute(sql,val)
        conn.commit()
    
    cur.close() 
    questions.clear()

    flash('Test was updated!',category='success')

    return redirect(url_for('groups.group',group_id = group_id))


