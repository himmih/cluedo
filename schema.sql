
-- super user have to execute in postgresql
/*
CREATE ROLE cluedo LOGIN
  PSSWORD '12345'
  NOSUPERUSER INHERIT CREATEDB NOCREATEROLE NOREPLICATION;
 CREATE DATABASE cluedo
  WITH OWNER = cluedo
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = -1;

-- after connect to cluedo database
 CREATE EXTENSION "uuid-ossp";
*/

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
