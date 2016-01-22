# playing cluedo game with friends that fare from you!
cluedo webapp for playing with your friends using mobile phones and any conference app(skype, hangouts etc.).
You need print and join with adhesive two board pices(see docs), print one cluedo notebook(see docs), two dices and no cards.

Для игры нужно распечатать табличку - notebook(см. в docs), распечатать и склеять поле - board(см. в docs), две игралные кости.
Играют минимум 3 максимум 6 игрока.

This is the flask (http://flask.pocoo.org) project.

<h3> Install </h3>

<h4>install postgresql </h4>

<b>in local postgresql: </b>

create pg user 'cluedo' with password 12345 (you can change it in cledo.py) and database

psql -c "CREATE ROLE cluedo LOGIN PASSWORD '12345';"

psql -c "CREATE DATABASE cluedo WITH OWNER = cluedo ENCODING = 'UTF8';"

psql -d cluedo -c 'create extension "uuid-ossp";'

<b>running app in dev mode: </b>
python cluedo.py

<b>init db </b>
run in browser http://localhost:5000/newgame

<b>The cluedo game is ready!</b> 

Every persons have to open http://<yourserver:5000
