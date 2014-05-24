import sqlite3
from flask import Flask, g
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


def add_user(username, email, pw_hash, timezone):
    insert_into('user', ['username','email', 'pw_hash', 'timezone'],[username, email, pw_hash, timezone])


def add_conversation(user1_id, user2_id, title, post_day, post_time):
    insert_into('conversation',['user1_id','user2_id', 'title', 'post_day','post_time'] ,[user1_id, user2_id, title, post_day, post_time])


def add_message(conversation_id, sender_id, receiver_id, message_text, message_timestamp, is_draft):
    insert_into('message', ['conversation_id','sender_id', 'receiver_id', 'message_text','message_timestamp','is_draft'],[conversation_id, sender_id, receiver_id, message_text, message_timestamp, is_draft])


def get_con():
    return get_db().cursor()


@app.teardown_request
def close_con():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
