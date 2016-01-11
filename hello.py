# -*- coding: utf-8 -*-
from types import *
import random, collections, sqlite3, json
from contextlib import closing
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
abort, render_template, flash, Response, make_response, jsonify

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

def get_game_db():
	return query_db("select id, players, opencards, hides from games where new = 1")

def create_game(players, my_color, my_name, game_mem):
    execute_db('insert into games(players, opencards, hides) values (?, ?, ?)',\
    [players, join_cards(game_mem[1]),join_cards(game_mem[0])])
    game_db = get_game_db()
    for i in range(players):
    	execute_db('insert into players(game_id, color, name, playercards, connected) values (?, ?, ?, ?, ?)',\
    	[game_db[0][0], my_color, my_name, join_cards(game_mem[2+i]), (i == 0)])
    
    opencards_ind = game_mem[1]
    opencards = dict(zip(opencards_ind, map(card_name, opencards_ind)))
    connected = get_connected_players(game_db);
    return {'players':players, 'connected':connected,\
    'opencards':opencards, 'playercards':dict(zip(game_mem[2], map(card_name, game_mem[2]))), 'color':my_color}

def join_game(game_db, my_color, my_name):

    #TODO MUST CHECK COLOR!!!
    #TODO MUST CHECK NAME!!!

    empty_player = query_db("select id, playercards from players where connected = 0 and game_id = ? limit 1", [game_db[0][0]])

    execute_db('update players set name = ?, color = ?, connected = 1 where id = ?',\
    [my_name, my_color,empty_player[0][0]])

    connected = get_connected_players(game_db);
    playercards_ind = split_cards(empty_player[0][1])
    playercards = dict(zip(playercards_ind, map(card_name, playercards_ind)))
    opencards_ind = split_cards(game_db[0][2])
    opencards = dict(zip(opencards_ind, map(card_name, opencards_ind)))

    return {'players':game_db[0][1], 'connected': connected, 'opencards':opencards,\
    'playercards': playercards, 'color':my_color}
	
def get_connected_players(game_db):
    if not game_db:
        game_db = get_game_db()
    if not game_db:
        return []
    connected = []
    for user in query_db('select color, name from players where connected = 1 and game_id = ?', [game_db[0][0]]):
            connected.append({'color':user[0], 'web_color':colors(user[0]), 'name': user[1]})
    for i in range(len(connected), game_db[0][1]):
        connected.append({'color': -1, 'web_color':'#aaaaaa', 'name': u'Ждем ...'})
    return connected

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
def colors(x):
    return {
         0: '#008000',
         1: '#ffdb58',
         2: '#000080',
         3: '#800080',
         4: '#ff2400',
         5: '#ffffff'
    }[x]
def card_name(x):
    return {
        'a0':'Мистер Грин'  ,
        'a1':'Мистер Мастард'  ,
        'a2':'Леди Пикок'  ,
        'a3':'Мистер Плам'  ,
        'a4':'Леди Скарлет'  ,
        'a5':'Леди Уайт'  ,
        'b0':'Гаечный ключ'  ,
        'b1':'Подсвечник'  ,
        'b2':'Кинжал'  ,
        'b3':'Револьвер'  ,
        'b4':'Свинцовая труба'  ,
        'b5':'Веревка'  ,
        'c0':'Ванная комната'  ,
        'c1':'Кабинет'  ,
        'c2':'Столовая'  ,
        'c3':'Бильярдная'  ,
        'c4':'Гараж'  ,
        'c5':'Спальня'  ,
        'c6':'Гостинная'  ,
        'c7':'Кухня'  ,
        'c8':'Внутренний двор',
    }[x]

def colors_from_connect(res, x):
     try:
             return res+[x['color']]
     except KeyError:
             return res
def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
#################### UTILS END ########################################

@app.route("/newgame")
def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
			db.commit()
        return 'ok'

@app.route("/", methods=['GET','POST'])
def hello():
	if request.method == 'POST' : #main
                game_db = get_game_db()
                if not game_db: # no game, create game
                    game_mem = generate_game(int(request.form['players'])) 	
                    out = create_game(int(request.form['players']), int(request.form['color' ]), request.form['name'], game_mem)
                    session ['color'] = out['color'] #fix player id
                    return render_template('main.html', game=out)
                else: # game exists, connect to it
                    out = join_game(game_db, int(request.form['color' ]), request.form['name'])
                    session ['color'] = int(request.form['color' ]) #fix player id
                    return render_template('main.html', game=out)
	else: # hello
		game_db = get_game_db()
	        if game_db:
	        	out = {'players':game_db[0][1]}
                        opencards_ind = split_cards(game_db[0][2])
    	        	out.update({"opencards" : dict(zip(opencards_ind, map(card_name, opencards_ind)))})	
                        freecolors = range(6)
    	        	connected = filter(lambda x: x['color'] > -1, get_connected_players(game_db))
                        freecolors = list( set(range(6)) - set(reduce(colors_from_connect, connected, [])) )
                        out.update({"connected" : connected})	
                        if (len(connected) < game_db[0][1]):
                            out.update({"freecolors": dict(zip(freecolors, map(colors,freecolors)))})
	        else:
	        	out = {}
                        out.update({"freecolors": dict(zip(range(6), map(colors, range(6))))})
		return render_template('hello.html', game=out)

@app.route("/getconnected")
def show_connected():
    out = json.dumps(get_connected_players(None), encoding='utf-8', ensure_ascii=False)
    resp = Response(response=out,
                status=200, \
                            mimetype="application/json")
    return(resp)

    

if __name__ == "__main__":
    app.debug = True
    app.run()
