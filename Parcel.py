from flask import Flask, render_template, redirect, url_for, request, g, session
from werkzeug import check_password_hash, generate_password_hash

import sqlite3
import database

app = Flask(__name__)

# Configuration
PATH = "Database.db"

app.config.from_object(__name__)


#homepage
@app.route('/')
def hello_world():
    # print database.get_db()
    return render_template('homepage.html')


#register page
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    error=None
    if request.method == 'POST':
        if not request.form['username']:
            error='Username is required'
        elif not request.form['email'] or '@' not in request.form['email']:
            error='Please enter a valid email address'
        elif not request.form['password']:
            error='Please enter a password'
        elif request.form['password'] !=request.form['password2']:
            error='Your passwords need to match'
        #check for username being identical here
        else:
            db=database.get_db()
            parameters=[request.form['username'], request.form['email'], generate_password_hash(request.form['password']),
                        request.form['timezone']]
            db.execute('insert into user (username, email, pw_hash, timezone) values (?,?,?,?)', parameters )
            db.commit()
            return redirect(url_for('login_page'))

    return render_template('register.html', error=error)


#login page
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    error=None
    #if g.user: return 'You have already been logged in'
    if request.method=='POST':
        user=database.query_db('select * from user where username=?', [request.form['username']], one=True)
        if user is None:
            error='wrong username'
        elif not check_password_hash(user['pw_hash'], request.form['password']):
            error='password wrong'
        else:
            session['user_id']=user['user_id']
            #directing to the messages page
            return redirect(url_for('show_messages', id=user['username']))
    return render_template('login.html', error=error)

#logout function
@app.route('/logout')
def logout_page():
    session.pop('user_id', None)
    return redirect(url_for('show_messages', id='you have successfully logged yourself out of the program, yay!'))



#tests stupid shit yay
@app.route('/messages', methods=['GET', 'POST'])
@app.route('/messages/<id>')
def show_messages(id=None):
    if request.method == 'GET':
        return render_template('template1.html', id=id)
    if request.method == 'POST':
        return render_template('template1.html', id=request.form['id'])


# tests redirect
@app.route('/bitches')
def test_redirect():
    return redirect(url_for('show_messages', id="google"))


#tests forms
@app.route('/forms', methods=['GET', 'POST'])
def forms_test():
    return render_template('template2.html')


# error thingy

@app.errorhandler(404)
def page_not_found(error):
    return 'The page you have requested is not able to be found you piece of awesomeness.'


if __name__ == '__main__':
    app.run(debug=True)