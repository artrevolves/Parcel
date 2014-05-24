from flask import Flask, render_template, redirect, url_for, request
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
@app.route('/register')
def register_page():
    # print database.get_db()
    return render_template('register.html')

#tests stupid shit yay
@app.route('/messages',methods=['GET','POST'])
@app.route('/messages/<id>')
def show_messages(id=None):
    if request.method=='GET':
        return render_template('template1.html',id=id)
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