from flask import Blueprint, render_template, request, redirect, url_for,flash
from .models import conn
from flask_login import current_user, login_required
from psycopg2.extras import DictCursor
from .groups import session

tests = Blueprint('tests', __name__)

@tests.route('/create-test',methods = ["POST","GET"])
@login_required
def create_test():
    if 'group_id' in session:

        group_id = session.get('group_id')

        if 'admin' in session:
            admin = session.get('admin')
        else:
            admin = False

        if request.method == 'POST':

            global questions
            questions = {}

            test_name = request.form.get('test_name')

            session['test_name'] = test_name
            session['max_question'] = 1
            
            return redirect(url_for('tests.create_questions',current_question = 1))

        else:

            return render_template('create_test.html',user = current_user,page = 'Group'
                                   ,group_id = group_id,admin = admin)
    
    else:
        return redirect(url_for('groups.groups_menu'))

@tests.route('/create-questions/<int:current_question>',methods = ["POST","GET"])
@login_required
def create_questions(current_question):

    if 'group_id' in session:
        group_id = session.get('group_id')

        if 'admin' in session:
            admin = session.get('admin')

        else:
            admin = False

        max_question = session.get('max_question')

        if request.method == 'POST':
            
            if request.form['action-btn'] == 'Delete question':
                return delete_question(current_question)
            
            elif request.form['action-btn'] == 'Add question':
                return add_question(current_question)

            elif request.form['action-btn'] == 'Create test':
                return save_question(current_question,'Complete')
            
            elif request.form['action-btn'] == '<<':
                return save_question(current_question,current_question -1)

            elif request.form['action-btn'] == '>>':
                return save_question(current_question,current_question + 1)
            
            else:
                number = request.form.get('action-btn')
                return save_question(current_question,number)

        else:
            return render_template('question_create.html',user = current_user,page = 'Group',admin = admin,
                                group_id = group_id,current_question = current_question
                                ,max_question = max_question,questions = questions)

    else:
        return redirect(url_for('groups.groups_menu'))


@tests.route('/edit-test',methods = ["POST","GET"])
@login_required
def edit_test(): 

    if 'group_id' in session:
        group_id = session.get('group_id')

        if 'admin' in session:
            admin = session.get('admin')

        else:
            admin = False

        return render_template('edit_test.html',user = current_user,page = 'Group',admin = admin,
                                group_id = group_id)

    else:
        return redirect(url_for('groups.groups_menu'))

@tests.route('/start-test/<int:test_id>/<int:current_question>',methods = ["POST","GET"])
@login_required
def start_test(test_id,current_question): 
    global answers

    if 'group_id' in session:
        group_id = session.get('group_id')

        if 'admin' in session:
            admin = session.get('admin')

        else:
            admin = False

        if 'test_id' not in session:
            session['test_id'] = test_id
            answers = {}

        if request.method == 'POST':
        
            if request.form['action-btn'] == 'Complete test':
                return save_answer(current_question,'results')
            
            elif request.form['action-btn'] == '<<':
                return save_answer(current_question,current_question - 1)

            elif request.form['action-btn'] == '>>':
                return save_answer(current_question,current_question + 1)
            
            else:
                number = request.form.get('action-btn')
                return save_answer(current_question,number)

        else:

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
        return redirect(url_for('groups.groups_menu'))

@tests.route('/test_results/<int:current_question>',methods = ["GET"])
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

        cur.execute(f"SELECT right_question,question_number FROM questions WHERE test_id = '{test_id}';")
        right_answers = cur.fetchall()

        cur.execute(f"SELECT * FROM questions WHERE test_id = '{test_id}'")
        questions = cur.fetchall()

        cur.close()

        number_questions = right_answers[-1]['question_number']

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
        return redirect(url_for('groups.groups_menu'))


@tests.route('/delete-test/<test_id>',methods = ["DELETE","GET"])
@login_required
def delete_test(test_id): 

    if 'group_id' in session:

        cur = conn.cursor(cursor_factory=DictCursor)

        cur.execute(f"DELETE FROM questions WHERE test_id='{test_id}';")

        cur.execute(f"DELETE FROM tests WHERE test_id='{test_id}';")

        conn.commit()
        cur.close()
        
        group_id = session.get('group_id')
        return redirect(url_for('groups.group',group_id = group_id))

    else:
        return redirect(url_for('groups.groups_menu'))


def add_question(current_question):

    max_question = session.get('max_question')
    session.pop('max_question' ,None)
    session['max_question'] = max_question +1

    return save_question(current_question,max_question + 1)

def save_question(current_question,next_question):
    global questions

    if current_question not in questions:
        print('we in',current_question)
        questions[current_question] = {}

    question = request.form.get('question')

    answer1 = request.form.get('answer1')
    answer2 = request.form.get('answer2')
    answer3 = request.form.get('answer3')
    answer4 = request.form.get('answer4')

    right_answer = request.form.get('right_answer')
    print(right_answer)

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

    print(questions)

    if next_question == 'Complete':
        return complete_test()

    return redirect(url_for('tests.create_questions',current_question = next_question))

def delete_question(current_question):
    global questions

    questions_change = []

    for question in questions:
        if question > current_question:
            questions_change.append(question)
    
    for number in questions_change:
        questions[number - 1] = questions.pop(number)

    max_question = session.get('max_question')

    if max_question > 1 :
        max_question -= 1
        session['max_question'] = max_question

    if current_question != 1 and max_question < current_question:
        return redirect(url_for('tests.create_questions',current_question = current_question - 1))

    else:
        return redirect(url_for('tests.create_questions',current_question = current_question ))

def complete_test():
    global questions

    test_name = session.get('test_name')
    group_id = session.get('group_id')
    max_question = session.get('max_question')
    user_id = current_user.id

    del session['test_name']
    del session['max_question']

    cur = conn.cursor(cursor_factory=DictCursor)

    sql = "INSERT INTO tests(test_name,group_id,number_questions) values(%s,%s,%s) RETURNING test_id"
    val = (f'{test_name}',f'{group_id}',f'{max_question}')
    cur.execute(sql,val)

    value_dict = cur.fetchone()
    test_id = value_dict['test_id']

    str_val = ('question','answer1','answer2','answer3','answer4','right_answer')

    for question in questions:
        
        sql = "INSERT INTO questions(question,asnwer1,asnwer2,asnwer3,asnwer4,right_question,test_id,user_id,question_number) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        val = (f'{questions[question][str_val[0]]}',f'{questions[question][str_val[1]]}'
        ,f'{questions[question][str_val[2]]}',f'{questions[question][str_val[3]]}'
        ,f'{questions[question][str_val[4]]}',f'{questions[question][str_val[5]]}',f'{test_id}'
        ,f'{user_id}',f'{question}')

        cur.execute(sql,val)
        conn.commit()
    
    cur.close() 
    questions.clear()

    return redirect(url_for('groups.group',group_id = group_id))

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

    return redirect(url_for('tests.start_test',test_id = test_id,current_question = next_question))
