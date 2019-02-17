PRAGMA foreign_keys=OFF;


DROP TABLE IF EXISTS theatres;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS performances;
DROP TABLE IF EXISTS tickets;

DROP TRIGGER IF EXISTS ticket_sale;

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
    imdb text, --foreign key -> movies
    start_date date,
    start_time time,
    performance_id text unique primary key,
    seats_left int,
    FOREIGN KEY (imdb) REFERENCES movies(imdb), --Might have to be the IMDB-key instead?
    FOREIGN KEY (theatre_name) REFERENCES theatres(theatre_name)
);
CREATE TABLE tickets
(
    identifier text unique primary key default (lower(hex(randomblob(16)))), --primary key
    performance_id text, -- OwO,
    username text,
    FOREIGN KEY (performance_id) REFERENCES performances(performance_id),
    FOREIGN KEY (username) REFERENCES customers(username)
);


CREATE TRIGGER IF NOT EXISTS ticket_sale
	AFTER INSERT
	ON tickets
	BEGIN
	    update performances
	    set seats_left = seats_left - 1
	    where performance_id = NEW.performance_id;
	END;


INSERT INTO movies(title, imdb, year, running_time) values('The Shape of Water', 'tt5580390', 2017, 142);
INSERT INTO movies(title, imdb, year, running_time) values('Moonlight', 'tt4975722', 2016, 175);
INSERT INTO movies(title, imdb, year, running_time) values('Spotlight', 'tt1895587', 2015, 202);
INSERT INTO movies(title, imdb, year, running_time) values('Birdman', 'tt2562232', 2014, 152);

INSERT INTO theatres VALUES('Kino',10);
INSERT INTO theatres VALUES('Södran',16);
INSERT INTO theatres VALUES('Skandia',100);

COMMIT;
