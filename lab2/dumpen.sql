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
    start_date date,
    start_time time,
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

INSERT INTO movies(title, imdb, year, running_time) values('The Shawshank Redemption', 'tt0111161', 1994, 142);
INSERT INTO movies(title, imdb, year, running_time) values('The Godfather', 'tt0068646', 1972, 175);
INSERT INTO movies(title, imdb, year, running_time) values('The Godfather: Part II', 'tt0071562', 1974, 202);
INSERT INTO movies(title, imdb, year, running_time) values('The Dark Knight', 'tt0468569', 2008, 152);
INSERT INTO movies(title, imdb, year, running_time) values('12 Angry Men', 'tt0050083', 1957, 96);
INSERT INTO movies(title, imdb, year, running_time) values('Schindler''s List', 'tt0108052', 1993, 195);
INSERT INTO movies(title, imdb, year, running_time) values('The Lord of the Rings: The Return of the King', 'tt0167260', 2003, 201);
INSERT INTO movies(title, imdb, year, running_time) values('Pulp Fiction', 'tt0110912', 1994, 154);
INSERT INTO movies(title, imdb, year, running_time) values('Fight Club', 'tt0137523', 1999, 139);
INSERT INTO movies(title, imdb, year, running_time) values('The Lord of the Rings: The Fellowship of the Ring', 'tt0120737', 2001, 178);
INSERT INTO movies(title, imdb, year, running_time) values('Forrest Gump', 'tt0109830', 1994, 142);
INSERT INTO movies(title, imdb, year, running_time) values('Inception', 'tt1375666', 2010, 148);
INSERT INTO movies(title, imdb, year, running_time) values('The Lord of the Rings: The Two Towers', 'tt0167261', 2002, 179);
INSERT INTO movies(title, imdb, year, running_time) values('One Flew Over the Cuckoo''s Nest', 'tt0073486', 1975, 133);
INSERT INTO movies(title, imdb, year, running_time) values('Goodfellas', 'tt0099685', 1990, 146);
INSERT INTO movies(title, imdb, year, running_time) values('The Matrix', 'tt0133093', 1999, 136);
INSERT INTO movies(title, imdb, year, running_time) values('Se7en', 'tt0114369', 1995, 127);
INSERT INTO movies(title, imdb, year, running_time) values('The Silence of the Lambs', 'tt0102926', 1991, 118);
INSERT INTO movies(title, imdb, year, running_time) values('It''s a Wonderful Life', 'tt0038650', 1946, 130);
INSERT INTO movies(title, imdb, year, running_time) values('Spider-Man: Into the Spider-Verse', 'tt4633694', 2018, 117);
INSERT INTO movies(title, imdb, year, running_time) values('Saving Private Ryan', 'tt0120815', 1998, 169);
INSERT INTO movies(title, imdb, year, running_time) values('The Usual Suspects', 'tt0114814', 1995, 106);
INSERT INTO movies(title, imdb, year, running_time) values('The Green Mile', 'tt0120689', 1999, 189);
INSERT INTO movies(title, imdb, year, running_time) values('Interstellar', 'tt0816692', 2014, 169);
INSERT INTO movies(title, imdb, year, running_time) values('Psycho', 'tt0054215', 1960, 109);
INSERT INTO movies(title, imdb, year, running_time) values('American History X', 'tt0120586', 1998, 119);
INSERT INTO movies(title, imdb, year, running_time) values('City Lights', 'tt0021749', 1931, 87);
INSERT INTO movies(title, imdb, year, running_time) values('Casablanca', 'tt0034583', 1942, 102);
INSERT INTO movies(title, imdb, year, running_time) values('Modern Times', 'tt0027977', 1936, 87);
INSERT INTO movies(title, imdb, year, running_time) values('The Pianist', 'tt0253474', 2002, 150);
INSERT INTO movies(title, imdb, year, running_time) values('The Departed', 'tt0407887', 2006, 151);
INSERT INTO movies(title, imdb, year, running_time) values('Back to the Future', 'tt0088763', 1985, 116);
INSERT INTO movies(title, imdb, year, running_time) values('Terminator 2: Judgment Day', 'tt0103064', 1991, 137);
INSERT INTO movies(title, imdb, year, running_time) values('Whiplash', 'tt2582802', 2014, 106);
INSERT INTO movies(title, imdb, year, running_time) values('Rear Window', 'tt0047396', 1954, 112);
INSERT INTO movies(title, imdb, year, running_time) values('The Lion King', 'tt0110357', 1994, 88);
INSERT INTO movies(title, imdb, year, running_time) values('Raiders of the Lost Ark', 'tt0082971', 1981, 115);
INSERT INTO movies(title, imdb, year, running_time) values('Gladiator', 'tt0172495', 2000, 155);
INSERT INTO movies(title, imdb, year, running_time) values('The Prestige', 'tt0482571', 2006, 130);
INSERT INTO movies(title, imdb, year, running_time) values('Apocalypse Now', 'tt0078788', 1979, 147);
INSERT INTO movies(title, imdb, year, running_time) values('Memento', 'tt0209144', 2000, 113);


INSERT INTO customers VALUES('jonas90','Jonas Eriksson','516b98488eff166d9f10c4af5003a0e4');
INSERT INTO customers VALUES('johanna91','Johanna Johansson','d87e991a1844439c25248886243b9d07');


insert into performances values('SF Lund','The Dark Knight','2019-02-14', '18:00',23712371);
insert into performances values('SF Lund','Inception','2019-02-16', '20:00',23115378);
insert into performances values('SF Lund','Interstellar','2019-03-01', '20:00',43375372);
insert into performances values('Kino Lund','Interstellar','2019-03-03', '19:00',82365932);
insert into performances values('Kino Lund', 'The Lion King', '2019-03-03', '16:00', 11322431);

insert into tickets(performance_id) values(82365932);
insert into tickets(performance_id) values(82365932);

insert into tickets(performance_id) values(23115378);
insert into tickets(performance_id) values(23115378);

insert into tickets(performance_id) values(11322431);

COMMIT;
