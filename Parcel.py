from flask import Flask, render_template, redirect, url_for, request
import sqlite3
from flask import g

app = Flask(__name__)

# Configuration

app.config.from_object(__name__)

PATH = "Database.db"
list = ['UserTable', ['username TEXT','id INTEGER','password TEXT','timezone TEXT','country TEXT','email TEXT']]

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(PATH)
    return db

def get_con():
    return get_db().cursor()

def create_db():
    con = get_con()

    try:
        con.execute('SELECT * FROM "' + list[0] + '"')
    except:
        query = 'CREATE TABLE "' + list[0] + '" (' + ','.join(list[1]) + ')'
        print query
        con.execute(query)
    get_db().commit()

def add_user(username,id,password,timezone,country,email):
    create_db()
    get_con().execute('INSERT INTO UserTable VALUES (?,?,?,?,?,?)', [username,id,password,timezone,country,email])
    get_db().commit()
@app.route('/')
def hello_world():
    return 'Super Awesome Application'

#tests stupid shit yay
@app.route('/messages',methods=['GET','POST'])
@app.route('/messages/<id>')
def show_messages(id=None):
    if request.method=='GET':
        add_user("testUser",'12',"1234","132","fdsaf","dsfa")
        return render_template('template1.html',id="fuckfuck")
    if request.method=='POST':
        return render_template('template1.html',id=request.form['id'])

# tests redirect
@app.route('/bitches')
def test_redirect():
    return redirect(url_for('show_messages',id="google"))

#tests forms
@app.route('/forms',methods=['GET','POST'])
def forms_test():
    return render_template('template2.html')


# error thingy

@app.errorhandler(404)
def page_not_found(error):
    return 'The page you have requested is not able to be found you piece of awesomeness.'


if __name__ == '__main__':
    app.run(debug=True)