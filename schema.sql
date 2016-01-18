--CREATE EXTENSION "uuid-ossp";

drop table if exists games;
create table games (
 -- id serial primary key,
 id uuid primary key DEFAULT uuid_generate_v4(),
 players integer not null,
 opencards text not null,
 hides text not null,
 new integer not null default 1 
);

drop table if exists players;
create table players (
 id uuid primary key  NOT NULL DEFAULT uuid_generate_v4(),
 game_id uuid REFERENCES games,
 color integer not null,
 name text not null,
 playercards text,
 connected integer not null default 0
);

drop table if exists shows;
create table shows (
 id uuid primary key NOT NULL DEFAULT uuid_generate_v4(),
 game_id uuid REFERENCES games,
 sender integer not null,
 receiver integer not null,
 card text not null,
 showed integer not null default 0
);

drop table if exists checks ;
create table checks (
 id uuid primary key NOT NULL DEFAULT uuid_generate_v4(),
 game_id uuid REFERENCES games,
 sender integer not null,
 receiver integer not null,
 cards text not null,
 showed integer not null default 0,
 good integer not null default 0
);
