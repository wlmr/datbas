PRAGMA foreign_keys=OFF;


DROP TABLE IF EXISTS theatres;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS performances;
DROP TABLE IF EXISTS tickets;

PRAGMA foreign_keys=ON;

BEGIN TRANSACTION;

CREATE TABLE theatres
(
    theatre_name text unique primary key, --primary
    capacity int
);



CREATE TABLE movies
(
    title text unique, --compound key with year
    imdb text primary key unique, --invented key, primary
    year int,
    running_time int
);


CREATE TABLE customers
(
    username text unique primary key, -- invented key, primary
    name text,
    pwd text
);

CREATE TABLE performances
(
    theatre_name text, --compound with start_time, foreign key -> theatres
    movie_title text, --foreign key -> movies
    start_time datetime,
    performance_id int unique primary key,
    FOREIGN KEY (movie_title) REFERENCES movies(title), --Might have to be the IMDB-key instead?
    FOREIGN KEY (theatre_name) REFERENCES theatres(theatre_name)
);
CREATE TABLE tickets
(
    identifier text unique primary key default (lower(hex(randomblob(16)))), --primary key
    performance_id int, -- OwO
    FOREIGN KEY (performance_id) REFERENCES performances(performance_id)
);

INSERT INTO theatres VALUES('SF Lund',160);
INSERT INTO theatres VALUES('Kino Lund',80);

INSERT INTO movies VALUES('The Dark Knight','tt8353619',2008,152);
INSERT INTO movies VALUES('The Lord of the Rings: The Return of the King','tt2164409',2003,201);
INSERT INTO movies VALUES('Inception','tt8378773',2010,148);
INSERT INTO movies VALUES('Interstellar','tt2326094',2014,169);

INSERT INTO customers VALUES('jonas90','Jonas Eriksson','516b98488eff166d9f10c4af5003a0e4');
INSERT INTO customers VALUES('johanna91','Johanna Johansson','d87e991a1844439c25248886243b9d07');


insert into performances values('SF Lund','The Dark Knight','2019-02-14 18:00:00',23712371);
insert into performances values('SF Lund','Inception','2019-02-16 20:00:00',23115378);
insert into performances values('SF Lund','Interstellar','2019-03-01 20:00:00',43375372);
insert into performances values('Kino Lund','Interstellar','2019-03-03 19:00:00',82365932);

insert into tickets values(hex(randomblob(16)), 82365932);
insert into tickets values(hex(randomblob(16)), 82365932);
insert into tickets values(hex(randomblob(16)), 82365932);
insert into tickets values(hex(randomblob(16)), 82365932);
insert into tickets values(hex(randomblob(16)), 82365932);

insert into tickets values(hex(randomblob(16)), 23115378);
insert into tickets values(hex(randomblob(16)), 23115378);
insert into tickets values(hex(randomblob(16)), 23115378);
insert into tickets values(hex(randomblob(16)), 23115378);



COMMIT;
