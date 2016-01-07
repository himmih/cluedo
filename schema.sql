drop table if exists games;
create table games (
 id integer primary key autoincrement,
 players integer not null,
 opencards text not null,
 hides text not null,
 new integer not null default 1 
);

drop table if exists players;
create table players (
 id integer primary key autoincrement,
 game_id integer not null,
 color integer not null,
 name text not null,
 playercards text,
 connected integer not null default 0
);

drop table if exists shows;
create table shows (
 id integer primary key autoincrement,
 game_id integer not null,
 sender integer not null,
 receiver integer not null,
 card integer not null,
 showed boolean not null
);

drop table if exists checks ;
create table checks (
 id integer primary key autoincrement,
 game_id integer not null,
 sender integer not null,
 receiver integer not null,
 cards integer[] not null,
 showed boolean not null,
 good boolean not null
);
