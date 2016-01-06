import sqlite3
import random
from contextlib import closing
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
abort, render_template, flash, Response

# configuration
DATABASE = 'database.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

cards = range(21)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
			db.commit()

def get_db():
	db = getattr(g, '_database' , None)
	if db is None:
		db = g._database = connect_db()
	return db


@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database' , None)
	if db is not None:
		db.close()

def query_db(query, args=(), one=False):
	cur = get_db().execute(query, args)
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv

@app.route("/players")
def get_players():
	def generate():
		for p in query_db('select * from players'):
			yield ''.join(p) + '<br>'	
	return Response(generate())

@app.route("/shows")
def get_shows():
	for sh in query_db('select * from shows'):
		None

@app.route("/checks")
def get_checks():
	for ch in query_db('select * from checks'):
		None


@app.route("/")
def hello():
	players = query_db('select * from players limit 1')
	return render_template('hello.html', players=players)







def newgame():
    random.shuffle(cards)
    n = int(request.args.get( 'n' , '3'))
    out = "hiden cards: " + str(cards.__getslice__(0,3)) + " for game with " + str(n) + " players"
    for i in range(n):
    	out += "<br> player #" + str(i) + " : " + str(cards.__getslice__( 3 + (18/n)*i, 3 + (18/n)*i + 18/n ))
    out += "<br> open cards: " + str(cards.__getslice__(3+(18/n)*n, 3+(18/n)*n+18%n))
    
    return out

if __name__ == "__main__":
    app.debug = True
    app.run()
