drop table if exists players;
create table players (
 game_id integer primary key autoincrement,
 color integer primary key not null,
 name text not null,
 players integer not null,
 playercards integer[] not null,
 opencards integer[],
 hides integer[] not null
);

drop table if shows ;
create table shows (
 id integer primary key autoincrement,
 game_id integer not null,
 from integer not null,
 to integer not null,
 card integer not null,
 showed boolean not null
);

drop table if checks ;
create table checks (
 id integer primary key autoincrement,
 game_id integer not null,
 from integer not null,
 to integer not null,
 cards integer[] not null,
 showed boolean not null,
 good boolean not null,
);
