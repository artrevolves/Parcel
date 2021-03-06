from sqlite3 import dbapi2 as sqlite3
from flask import g
import time
from Parcel import app

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['PATH'])
        db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def insert_into(table, fields, args=[]):
    db = get_db()
    db.execute('INSERT INTO ' + table +" ("+ ','.join(fields) + ') VALUES (' + ','.join(['?' for x in xrange(len(args))]) + ')', args)
    db.commit()

def replace_message(text, conversation_id,sender,receiver):
    db = get_db()
    max_id =  db.execute("SELECT max(message_id) from message where conversation_id = ?",[conversation_id]).next()[0]
    if max_id is None:
        add_message(conversation_id,sender,receiver,text,time.time(),0)
    else:
        db.execute("UPDATE message SET message_text=? WHERE message_id = ?",[text,max_id])
        db.commit()


def add_user(username, email, pw_hash, timezone):
    insert_into('user', ['username','email', 'pw_hash', 'timezone'],[username, email, pw_hash, timezone])


def add_conversation(user1_id, user2_id, title, conversation_timestamp):
    insert_into('conversation',['user1_id','user2_id', 'title','conversation_timestamp'] ,[user1_id, user2_id, title, conversation_timestamp])


def get_users_conversations(user_id):
    return query_db("select * from conversation where user_id = ? or user2_id = ?",[user_id,user_id])

def get_conversation_messages(conversation_id):
    return query_db("select * from message where conversation_id = ?", conversation_id)

def add_message(conversation_id, sender_id, receiver_id, message_text, message_timestamp, is_draft):
    insert_into('message', ['conversation_id','sender_id', 'receiver_id', 'message_text','message_timestamp','is_draft'],[conversation_id, sender_id, receiver_id, message_text, message_timestamp, is_draft])


def get_con():
    return get_db().cursor()


@app.teardown_request
def close_con():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()