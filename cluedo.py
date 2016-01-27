# -*- coding: utf-8 -*-
from types import *
import random, collections, json, psycopg2, psycopg2.extensions
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
abort, render_template, flash, Response, make_response, jsonify
from flask_socketio import SocketIO

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

# configuration
DATABASE = 'dbname=cluedo user=cluedo password=12345'
DEBUG = True
SECRET_KEY = 'jambajambasecretkey17'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config.from_object(__name__)
socketio = SocketIO(app)

#################### DB WORK ########################################

def connect_db():
        return psycopg2.connect(app.config['DATABASE'])


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
	with get_db().cursor() as cur:
            cur.execute(query, args)
            rv = cur.fetchall()
	    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
	with get_db().cursor() as cur:
            cur.execute(query, args)
	    get_db().commit()

def insert_return_id(query, args=()):
	with get_db().cursor() as cur:
	    cur.execute(query + ' RETURNING id', args)
	    get_db().commit()
	    return cur.fetchone()[0]

#################### DB WORK END ########################################

#################### DB SHOW ########################################
@app.route("/_games")
def get_games():
	out = ""
	for game in query_db('select * from games'):
		out += str(game) + '<br>'	
	return(out)

@app.route("/_players")
def get_players():
	out = ""
	for player in query_db('select * from players'):
		out += str(player) + '<br>'	
	return(out)

@app.route("/_shows")
def get_shows():
	out = ""
	for show in query_db('select * from shows'):
		out += str(show) + '<br>'	
	return(out)

@app.route("/_checks")
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

def get_game_db(id=None): #TODO remove invoke without id
        if id:
            return query_db("select id, players, opencards, hides from games where id = %s", [id])
        else:
            return query_db("select id, players, opencards, hides from games where new = 1")

def create_game(players, my_color, my_name, game_mem):
    game_id = insert_return_id('insert into games(players, opencards, hides) values (%s, %s, %s)',\
    [players, join_cards(game_mem[1]),join_cards(game_mem[0])])
    game_db = get_game_db(game_id)
    for i in range(players):
    	execute_db('insert into players(game_id, color, name, playercards, connected) values (%s, %s, %s, %s, %s)',\
    	[game_db[0][0], my_color, my_name, join_cards(game_mem[2+i]), 1 if (i == 0) else 0])
    
    opencards_ind = game_mem[1]
    opencards = dict(zip(opencards_ind, map(card_name, opencards_ind)))
    connected = get_connected_players(game_db);
    return {'game_id': game_db[0][0],'players':players, 'connected':connected,\
    'opencards':opencards, 'playercards':dict(zip(game_mem[2], map(card_name, game_mem[2]))), 'color':my_color}

def join_game(game_db, my_color, my_name):
    connected = filter(lambda x: x['color'] > -1, get_connected_players(game_db))

    #TODO MUST CHECK NAME!!!
    if my_name in reduce(names_from_connect, connected, []):
        my_name = my_name + u'ц'

    #TODO MUST CHECK COLOR!!!
    freecolors = list( set(range(6)) - set(reduce(colors_from_connect, connected, [])) )
    if not my_color in freecolors:
       my_color = freecolors[0] 

    empty_player = query_db("select id, playercards from players where connected = 0 and game_id = %s limit 1", [game_db[0][0]])

    if empty_player:
        execute_db('update players set name = %s, color = %s, connected = 1 where id = %s',\
        [my_name, my_color,empty_player[0][0]])

        connected = get_connected_players(game_db);
        playercards_ind = split_cards(empty_player[0][1])
        playercards = dict(zip(playercards_ind, map(card_name, playercards_ind)))
        opencards_ind = split_cards(game_db[0][2])
        opencards = dict(zip(opencards_ind, map(card_name, opencards_ind)))

        return {'players':game_db[0][1], 'connected': connected, 'opencards':opencards,\
        'playercards': playercards, 'color':my_color}
    else:
        return None

def get_main(game_id, user_color):

    game_db = get_game_db(game_id)
    player = query_db("select id, playercards from players where color = %s and game_id = %s", [user_color, game_db[0][0]])

    connected = get_connected_players(game_db);
    playercards_ind = split_cards(player[0][1])
    playercards = dict(zip(playercards_ind, map(card_name, playercards_ind)))
    opencards_ind = split_cards(game_db[0][2])
    opencards = dict(zip(opencards_ind, map(card_name, opencards_ind)))

    return {'players':game_db[0][1], 'connected': connected, 'opencards':opencards,\
    'playercards': playercards, 'color':user_color}
	
def get_connected_players(game_db):
    #TODO get only by id!
    if not game_db:
        game_db = get_game_db()
    if not game_db:
        return []
    connected = []
    for user in query_db('select color, name from players where connected = 1 and game_id = %s', [game_db[0][0]]):
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
         0: '#53aa53',
         1: '#ffe88f',
         2: '#5353aa',
         3: '#aa53aa',
         4: '#ff6b53',
         5: '#ffffff'
    }[x]
def card_name(x):
    return {
        'a0':u'Мистер Грин'  ,
        'a1':u'Мистер Мастард'  ,
        'a2':u'Леди Пикок'  ,
        'a3':u'Мистер Плам'  ,
        'a4':u'Леди Скарлет'  ,
        'a5':u'Леди Уайт'  ,
        'b0':u'Гаечный ключ'  ,
        'b1':u'Подсвечник'  ,
        'b2':u'Кинжал'  ,
        'b3':u'Револьвер'  ,
        'b4':u'Свинцовая труба'  ,
        'b5':u'Веревка'  ,
        'c0':u'Ванная комната'  ,
        'c1':u'Кабинет'  ,
        'c2':u'Столовая'  ,
        'c3':u'Бильярдная'  ,
        'c4':u'Гараж'  ,
        'c5':u'Спальня'  ,
        'c6':u'Гостинная'  ,
        'c7':u'Кухня'  ,
        'c8':u'Внутренний двор',
    }[x]

def colors_from_connect(res, x):
     try:
             return res+[x['color']]
     except KeyError:
             return res

def names_from_connect(res, x):
     try:
             return res+[x['name']]
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
	with app.open_resource('schema.sql', mode='r') as f:
		with get_db().cursor() as cur:
		    cur.execute(f.read())
	get_db().commit()
        return 'ok'

@app.route("/", methods=['GET','POST'])
def hello():
	if request.method == 'POST' : #main
                game_db = get_game_db()
                session.permanent = True
                if not game_db: # no game, create game
                    game_mem = generate_game(int(request.form['players'])) 	
                    out = create_game(int(request.form['players']), int(request.form['color' ]), request.form['name'], game_mem)
                    session ['color'] = out['color']
                    session ['game'] = out['game_id']
                    return render_template('main.html', game=out)
                else: # game exists, connect to it
                    out = join_game(game_db, int(request.form['color' ]), request.form['name'])
                    if out:
                        session ['color'] = int(out['color'])
                        session ['game'] = game_db[0][0] 
                        return render_template('main.html', game=out)
                    else:
                        return redirect('/', code=302)
	else: # hello
		game_db = get_game_db()
                if not game_db or game_db[0][0] != session.get('game', None) or session.get('color', None) == None:
                    if game_db:
                            out = {'players':game_db[0][1]}
                            opencards_ind = split_cards(game_db[0][2])
                            out.update({"opencards" : dict(zip(opencards_ind, map(card_name, opencards_ind)))})	
                            connected = filter(lambda x: x['color'] > -1, get_connected_players(game_db))
                            freecolors = list( set(range(6)) - set(reduce(colors_from_connect, connected, [])) )
                            out.update({"connected" : connected})	
                            if (len(connected) < game_db[0][1]):
                                out.update({"freecolors": dict(zip(freecolors, map(colors,freecolors)))})
                    else:
                            out = {"freecolors": dict(zip(range(6), map(colors, range(6))))}
                    return render_template('hello.html', game=out)
                else:
                    out = get_main(session.get('game', None), session.get('color', None)) 
                    return render_template('main.html', game=out)

@app.route("/getconnected")
def show_connected():
    out = json.dumps(get_connected_players(None), encoding='utf-8', ensure_ascii=False)
    resp = Response(response=out,
                status=200, \
                            mimetype="application/json")
    return(resp)

@app.route("/show", methods=['GET','POST'])
def push_show():
        my_color = session.get('color') #TODO if not redirect to /
	game_db = get_game_db() #TODO check against session.get('game', None)
        if not game_db:
         return redirect('/', code=302)
            
	if request.method == 'POST' : #main
            #TODO check inputs
            #TODO show checks!
            card = request.form['card']
            receiver = int(request.form['color'])
    	    execute_db('insert into shows(game_id, sender, receiver, card, showed) values (%s, %s, %s, %s, %s)',\
    	    [game_db[0][0], my_color, receiver, card, 0])
            return redirect('/', code=302)
        else: #TODO check if no not check result the game not end!
            out = get_show(my_color, game_db[0][0], game_db)
            if (out):
                showed_show(json.loads(out).get('id'))
            else:
                out = get_check(my_color, game_db[0][0], game_db)
                if (out):
                    showed_check(json.loads(out).get('id'))
                else:
                    out = json.dumps({})
            return(Response(response=out, status=200, mimetype="application/json"))

def get_show(my_color, game_id, game_db = None): #TODO need to redirect to new game????
        if not game_db: game_db = get_game_db(game_id)
        show = query_db("select id, card, sender from shows where receiver = %s and game_id = %s and showed = 0 limit 1", [my_color, game_db[0][0]])
        if len(show) > 0:
            sender_name = query_db("select name from players where color = %s and game_id = %s limit 1", [show[0][2], game_db[0][0]])
            out = json.dumps({ 'id': show[0][0], 'card':show[0][1], 'sender':show[0][2],\
            'sender_name': sender_name[0][0], 'card_name':card_name(show[0][1])}, encoding='utf-8', ensure_ascii=False)
            return out
        else:
            return None

def showed_show(show_id): #callback=ack
        if (show_id):
            execute_db('update shows set showed = %s where id = %s', [1, show_id])

def get_check(my_color, game_id, game_db = None):
        if not game_db: game_db = get_game_db(game_id)
        check = query_db("select id, cards, sender, good from checks where receiver = %s and game_id = %s and showed = 0 limit 1", [my_color, game_db[0][0]])
        if len(check) > 0:
            sender_name = query_db("select name from players where color = %s and game_id = %s limit 1", [check[0][2], game_db[0][0]])
            out = json.dumps({ 'id': check[0][0], 'cards':check[0][1], 'good': check[0][3], 'sender':check[0][2],\
            'sender_name': sender_name[0][0], 'cards_name':map(card_name, split_cards(check[0][1]))}, encoding='utf-8', ensure_ascii=False)
            return out
        else:
            return None

def showed_check(check_id): #callback=ack
            if len(check_id) > 0:
                checks = query_db("select good, receiver, game_id from checks where id = %s", [check_id]) #is_good_check, my_color, game_id
                if len(checks) > 0:
                    execute_db('update checks set showed = %s where id = %s', [1, check_id])
                    if (checks[0][0] == 1): 
                        nobody_else = query_db("select id from checks where receiver != %s and game_id = %s and showed = 0 limit 1", [checks[0][1], checks[0][2]])
                        if len(nobody_else) < 1: execute_db('update games set new = 0 where id = %s', [checks[0][2]])
            
@app.route("/check", methods=['GET','POST'])
def check():
        my_color = session.get('color') #TODO if not redirect to /
	game_db = get_game_db() #TODO check against session.get('game', None)
	if request.method == 'POST' : #main
            hides = query_db("select hides from games where id = %s", [game_db[0][0]])
            cards = map(lambda x: x.encode('utf-8'), [request.form['card_a'], request.form['card_b'], request.form['card_c']])
            good = 1 if split_cards(hides[0][0]) == cards else 0
            players = query_db("select color from players where game_id = %s", [game_db[0][0]])
            for player_color in zip(*players)[0]:
                execute_db('insert into checks(game_id, sender, receiver, cards, showed, good) values (%s, %s, %s, %s, %s, %s)',\
                [game_db[0][0], my_color, player_color, join_cards(cards), 0, good])
            return redirect('/', code=302)
        else:
            return render_template('check.html', game=my_color)
    


if __name__ == "__main__":
    #app.debug = True
    socketio.run(app, host='0.0.0.0') #host='176.58.109.138', port=4242)
