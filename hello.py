from flask import Flask, request
import random
app = Flask(__name__)

cards = range(21)

@app.route("/")
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
