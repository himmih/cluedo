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

#################### DB WORK ########################################

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

def execute_db(query, args=()):
	get_db().execute(query, args)
	get_db().commit()

#################### DB WORK END ########################################

#################### DB SHOW ########################################
@app.route("/games")
def get_games():
	out = ""
	for game in query_db('select * from games'):
		out += str(game) + '<br>'	
	return(out)

@app.route("/players")
def get_players():
	out = ""
	for player in query_db('select * from players'):
		out += str(player) + '<br>'	
	return(out)

@app.route("/shows")
def get_shows():
	out = ""
	for show in query_db('select * from shows'):
		out += str(show) + '<br>'	
	return(out)

@app.route("/checks")
def get_checks():
	out = ""
	for ch in query_db('select * from checks'):
		out += str(ch) + '<br>'	
	return(out)

#################### DB SHOW END ########################################



#################### UTILS ########################################
def join_cards(lcards):
	return repr(lcards)

def split_cards(scards):
	return eval(scards)

def new_game_exists():
    game_id = query_db('select id from game where new')
    if game_id:
    	return True
    else:
    	return False

def create_game(players, my_color, my_name, game):
    execute_db('insert into games(players, opencards, hides) values (?, ?, ?)',\
    [players, join_cards(game[1]),join_cards(game[0])])
    game_id = query_db("select id from games where new = 1")
    print str(game_id) 
    for i in range(players):
    	execute_db('insert into players(game_id, color, name, playercards, connected) values (?, ?, ?, ?, ?)',\
    	[game_id[0][0], my_color, my_name, join_cards(game[2+i]), (i == 0)])
    return {'players':players, 'connected':{'color':my_color, 'name':my_name}, 'opencards':game[1], 'playercards':game[2], 'color':my_color}
	

def generate_game(n = 3):
    who = []
    for i in range(6):
    	who.append('a'+ str(i))
    random.shuffle(who)

    withwhat = []
    for i in range(6):
    	withwhat.append('b'+ str(i))
    random.shuffle(withwhat)

    where = []
    for i in range(9):
    	where.append('c'+str(i))
    random.shuffle(where)

    hiden =[who.pop(0), withwhat.pop(0), where.pop(0)] #hiden cards
    out = [hiden]

    cards = who + withwhat + where
    random.shuffle(cards)

    out.append(cards.__getslice__((18/n)*n, (18/n)*n+18%n)) #open cards out[1]

    for i in range(n):
	out.append(cards.__getslice__( (18/n)*i, (18/n)*i + 18/n )) #player's cards out[2..]

    return out
#################### UTILS END ########################################

@app.route("/", methods=['GET','POST'])
def hello():
	if request.method == 'POST' :
	        game = generate_game(int(request.form['players'])) 	
		out = create_game(int(request.form['players']), int(request.form['color' ]), request.form['name'], game)
		return render_template('main.html', out=out)
	else:
		# left colors
		if new_game_exists(): #TODO
			return render_template('hello.html', players=None)
		else:
			return render_template('hello.html', players=None)

if __name__ == "__main__":
    app.debug = True
    app.run()
