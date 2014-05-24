############################################################################
## PARCEL
##   for Hack UCI
############################################################################

from flask import Flask, render_template, redirect, url_for, request, g, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

import database

app = Flask(__name__)

# Configuration
PATH = "Database.db"
SECRET_KEY = "sdafdsafdasfdsafsdaf"

app.config.from_object(__name__)

app.secret_key = app.config['SECRET_KEY']

# --------------------------------------------------------------------------
# HOME PAGE
# --------------------------------------------------------------------------
@app.route('/')
def home_page():
    return render_template('homepage.html')

# Grab the current logged in user at the beginning of each request.
# Use g.user whenever you want to access the currently logged in user
@app.before_request
def fetch_user():
    g.user = None
    if 'user_id' in session:
        g.user = database.query_db('select * from user where user_id=?',
                                   [session['user_id']], one=True)

# --------------------------------------------------------------------------
# REGISTRATION PAGE
# --------------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    # if user is logged in, don't let them see the page at all
    if g.user: return show_message('You already have an account here, moron')
    
    if request.method == 'POST':
        if not request.form['username']:
            return render_template('register.html', error="Username is required")
        elif not request.form['email'] or '@' not in request.form['email']:
            return render_template('register.html', error="Please enter a valid email")
        elif not request.form['password']:
            return render_template('register.html', error="Please enter a password")
        elif request.form['password'] != request.form['password2']:
            return render_template('register.html', error=" Please make sure your passwords match")
        # TODO: check for username being identical here
        
        db=database.get_db()
        database.add_user(request.form['username'], 
                          request.form['email'], 
                          generate_password_hash(request.form['password']), 
                          request.form['timezone'])
                          
        return redirect(url_for('login_page'))

    return render_template('register.html')

# --------------------------------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # if user is logged in, don't let them see the page at all
    if g.user: return show_message('You have already been logged in, ' + g.user['username'])
    
    if request.method=='POST':
        user = database.query_db('select * from user where username=?', 
                                 [request.form['username']], one=True)
                                 
        if user is None:
            return render_template('login.html', error="Username or password is incorrect")
        
        if not check_password_hash(user['pw_hash'], request.form['password']):
            return render_template('login.html', error="Username or password is incorrect")

        session['user_id'] = user['user_id']
        return show_message("Oh hai " + str(user['username']))
        
    return render_template('login.html')

# --------------------------------------------------------------------------
# LOGOUT PAGE
# --------------------------------------------------------------------------
@app.route('/logout')
def logout_page():
    session.pop('user_id', None)
    return show_message("You have successfully logged yourself out!")

# --------------------------------------------------------------------------
# MESSAGE PAGE (FOR DEBUGGING)
# --------------------------------------------------------------------------
@app.route('/message')
def show_message(message=None):
    return render_template("message.html", message=message)

# --------------------------------------------------------------------------
# 404 PAGE
# --------------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(error):
    return error

if __name__ == '__main__':
    app.run(debug = True)