############################################################################
## PARCEL
##   for Hack UCI
############################################################################

from flask import Flask, render_template, redirect, url_for, request, g, session
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import time

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

@app.template_filter()
def username_from_id(id):
    q = database.query_db('select * from user where user_id=?',
                      [id], one=True)
    return "n/a" if not q else q["username"]
    
@app.template_filter()
def pretty_date(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp).strftime("%m/%d/%Y %H:%M")
    
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
    
    if request.method == 'POST':
        user = database.query_db('select * from user where username=?', 
                                 [request.form['username']], one=True)
                                 
        if user is None:
            return render_template('login.html', error="Username or password is incorrect")
        
        if not check_password_hash(user['pw_hash'], request.form['password']):
            return render_template('login.html', error="Username or password is incorrect")

        session['user_id'] = user['user_id']
        return redirect(url_for("conv_list_page"))
        
    return render_template('login.html')

# --------------------------------------------------------------------------
# LOGOUT PAGE
# --------------------------------------------------------------------------
@app.route('/logout')
def logout_page():
    session.pop('user_id', None)
    return redirect(url_for("home_page"))

# --------------------------------------------------------------------------
# CONVERSATION LIST PAGE
# --------------------------------------------------------------------------
@app.route('/conversations')
def conv_list_page():
    if not g.user: return show_message('You need to be logged in to see this page.')
    
    items = database.query_db("select * from conversation where user1_id=? or user2_id=?", 
    [g.user['user_id'], g.user['user_id']])
    return render_template('conv_list.html', conversations=items)
    
# --------------------------------------------------------------------------
# CONVERSATION ADDING PAGE
# --------------------------------------------------------------------------
@app.route('/conv_add', methods=['GET', 'POST'])
def conv_add_page():
    if not g.user: return show_message('You need to be logged in to see this page.')
    
    if request.method == 'POST':
        if not request.form['title']:
            return render_template('conv_add.html', error="Please name your conversation")
        elif not request.form['recipient']:
            return render_template('conv_add.html', error="You need someone else in this conversation")

        id = database.query_db("select user_id from user where username=?", [request.form['recipient']], one=True)
        if not id:
            return render_template('conv_add.html', error="Recipient username does not exist")
        else:
            id = id[0]
        
        database.add_conversation(g.user['user_id'], id, request.form['title'], time.time())
        
        return redirect(url_for("conv_list_page"))
        
    return render_template('conv_add.html') 

# --------------------------------------------------------------------------
# CONVERSATION VIEW PAGE
# --------------------------------------------------------------------------
@app.route('/conv_view/<conv_id>', methods=['GET', 'POST'])
def conv_view(conv_id=None):
    if not g.user: return show_message('You need to be logged in to see this page.')

    conversation = database.query_db("select * from conversation where conversation_id=?",
                                     [conv_id], one=True)

    # posting a draft
    if request.method == 'POST':
        database.replace_message(request.form["text"],conv_id,g.user["user_id"],conversation["user2_id"])
        # database.add_message(conv_id,
        #                      g.user["user_id"],
        #                      conversation["user2_id"],
        #                      request.form["text"],
        #                      int(time.time()),
        #                      0)
        return redirect('/conv_view/'+conv_id)

    messages = database.query_db("select * from message where conversation_id=? order by message_timestamp desc",
                                 [conv_id])
    hide_editor=False
    if len(messages)>0:
        if messages[0]['sender_id'] != g.user['user_id']:#Hide draft post if use does not own it
            messages.pop(0)
            hide_editor = True

    return render_template('conv_view.html', conversation=conversation, messages=messages, hide_editor=hide_editor)

# --------------------------------------------------------------------------
# USER LIST PAGE (FOR DEBUGGING)
# --------------------------------------------------------------------------
@app.route('/user_list')
def show_user_list(message=None):
    return render_template("user_list.html", users=database.query_db("select * from user"))
    
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
        app.run(debug = True    )