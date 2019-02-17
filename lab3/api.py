from bottle import get, post, run, request, response
import sqlite3
import json
import os
from hashlib import sha256

import logging


def get_logging_instance(name: str,
                         level: int = logging.DEBUG) -> logging.Logger:
    lg = logging.getLogger(name)
    lg.setLevel(level)
    stream = logging.StreamHandler()
    stream.setLevel(level)
    stream.setFormatter(logging.Formatter('[%(asctime)s] [%(name)s.%(funcName)s] : %(message)s'))
    lg.addHandler(stream)
    return lg


logger: logging.Logger = get_logging_instance(__name__)

HOST = 'localhost'
PORT = 4568

_schema_path = 'schemas'

conn = sqlite3.connect("applications.sqlite")


def _hash(text: str,
          max_len: int = None) -> str:
    sh = sha256()
    sh.update(text.encode(encoding='utf-8'))
    val = sh.hexdigest()
    logger.debug(f"plaintext \"{text}\" hashed into \"{val}\"")
    return val if not max_len else val[:max_len]


def _sanitize(text: str) -> str:
    return text.replace("'", "''")


def url(resource):
    return f"http://{HOST}:{PORT}{resource}"


def format_response(d):
    return json.dumps(d, indent=4) + "\n"


@get('/ping')
def ping():
    logger.debug('Ping recieved!')
    return "pong"


@post('/reset')
def reset():
    logger.debug("Reset recieved!")
    cursor = conn.cursor()
    with open(os.path.join(_schema_path, 'reset.sql'), 'r') as f:
        sqls = f.read()
    conn.executescript(sqls)

    users = (('alice', 'Alice', 'dobido'),
             ('bob', 'Bob', 'whatsinaname'))
    for uname, name, plainpwd in users:
        command = f"INSERT INTO customers(username, name, pwd) values('{uname}', '{name}', '{_hash(plainpwd)}')"
        logger.info("Executing {}".format(command))
        cursor.execute(command)
    conn.commit()
    response.status = 200
    return "OK"


@get('/movies')
def get_movies():
    response.content_type = 'application/json'
    curs = conn.cursor()

    params = []
    sql_query = "select imdb, title, year from movies where 1 = 1"
    if request.query.title:
        sql_query += ' and title = ?'
        params.append(request.query.title)
    if request.query.year:
        sql_query += ' and year = ?'
        params.append(request.query.year)
    curs.execute(sql_query, params)
    res = [{"title": t, "imdb": imdb, "year": y} for imdb, t, y in curs]
    response.status = 200
    return format_response({"data": res})


@get('/movies/<imdb>')
def get_movies(imdb):
    response.content_type = 'application/json'
    curs = conn.cursor()
    curs.execute('select imdb, title, year from movies where imdb = ?', [imdb])
    res = [{"title": t, "imdb": i, "year": y} for i, t, y in curs]
    response.status = 200
    return format_response({"data": res})


# noinspection SpellCheckingInspection
@post('/performances')
def add_performance():
    curs = conn.cursor()

    def _count(table, column, parameter):
        curs.execute(f"select count() from {table} where {column} = ?", [parameter])
        r = curs.fetchall()[0][0]
        return r

    imdb = request.query.imdb
    theater = request.query.theater
    date = request.query.date
    time = request.query.time
    if not all((imdb, theater, date, time)):
        response.status = 400
        return "Missing attributes in request!"
    # Looking for movie
    imdb = _sanitize(imdb)
    theater = _sanitize(theater)
    date = _sanitize(date)
    time = _sanitize(time)
    if _count('movies', 'imdb', imdb) == 0:
        response.status = 404
        msg = f"No movie with imdb \"{imdb}\""
        logger.error(msg)
        return msg
    elif _count('theatres', 'theatre_name', theater) == 0:
        response.status = 404
        msg = f"No Theater with name \"{theater}\""
        logger.error(msg)
        return msg
    unique_performance = _hash(''.join((theater, imdb, date, time)), max_len=16)  # simple, but it should work just fine
    print(len(unique_performance))
    if _count('performances', 'performance_id', unique_performance) > 0:
        response.status = 404
        msg = f"The performance with id \"{unique_performance}\" already exists!"
        logger.error(msg)
        return msg
    curs.execute(f"select capacity from theatres where theatre_name = '{theater}'")
    nbr_seats = curs.fetchall()[0][0]
    command = f"insert into performances values('{theater}', '{imdb}', " \
              f"'{date}', '{time}', '{unique_performance}', {nbr_seats})"
    logger.debug(command)
    curs.execute(command)
    conn.commit()
    response.status = 200
    return_message = f"/performances/{unique_performance}"
    return return_message


# noinspection SpellCheckingInspection
@get('/performances')
def get_performances():
    response.content_type = 'application/json'
    curs = conn.cursor()
    curs.execute("select p.performance_id, p.start_date, p.start_time, m.title, m.year, "
                 "p.theatre_name, p.seats_left from movies m, performances p "
                 "where m.imdb = p.imdb group by p.performance_id;")
    res = [{"performanceId": pid, "date": date, "startTime": time,
            "title": title, "year": year, "theater": theatre, "remainingSeats": seats}
           for pid, date, time, title, year, theatre, seats in curs]
    response.status = 200
    return format_response({"data": res})


@post('/tickets')
def buy_ticket():
    curs = conn.cursor()

    def seats_left(p):
        curs.execute("select seats_left from performances where performance_id = ?", [p])
        _result = curs.fetchall()[0][0]
        return _result > 0

    def passwords_match(_usr, _hashed_pwd):
        curs.execute("select pwd from customers where username = ?", [_usr])
        _result = curs.fetchall()[0][0]
        return _result == _hashed_pwd

    def exists_user(_usr):
        curs.execute("select count() from customers where username = ?", [_usr])
        _result = curs.fetchall()[0][0]
        return _result > 0

    def exists_performance(_performance):
        curs.execute("select count() from performances where performance_id = ?", [_performance])
        _result = curs.fetchall()[0][0]
        return _result > 0

    usr = request.query.user
    performance = request.query.performance
    pwd = request.query.pwd
    logger.debug("Checking arguments")
    if not all((usr, performance, pwd)):
        response.status = 400
        return "Missing attributes in request!"

    usr = _sanitize(usr)
    performance = _sanitize(performance)
    pwd = _sanitize(pwd)
    logger.debug("Checking if user exists or performance exists")
    if not exists_user(usr) or not exists_performance(performance):
        response.status = 404
        return "Error"

    logger.debug("Checking if there are seats left")
    if not seats_left(performance):
        response.status = 404
        return "No tickets left"

    hashed_pwd = _hash(pwd)

    logger.debug("Checking if passwords match")

    if not passwords_match(usr, hashed_pwd):
        response.status = 404
        return "Wrong password"

    curs.execute(f"insert into tickets(performance_id, username) values('{performance}', '{usr}')")
    conn.commit()

    curs.execute("select identifier from tickets where rowid = last_insert_rowid()")
    id_string = curs.fetchall()[0][0]
    response.status = 200
    return f"/tickets/{id_string}"


@get('/customers/<customer>/tickets')
def get_tickets(customer):
    response.content_type = 'application/json'
    # TODO! nicer sql statement!
    curs = conn.cursor()
    customer = _sanitize(customer)
    curs.execute("select performance_id from tickets where username = ? group by performance_id", [customer])
    performances = [x[0] for x in curs.fetchall()]
    total = []
    for performance in performances:
        curs.execute("select count () from tickets where performance_id = ? and username = ?", [performance, customer])
        tickets_taken = curs.fetchall()[0][0]
        curs.execute("select theatre_name, start_date, start_time, imdb from performances where performance_id = ?",
                     [performance])
        theatre, date, time, imdb = curs.fetchone()
        curs.execute("select title, year from movies where imdb = ?", [imdb])
        title, year = curs.fetchone()
        total.append({"date": date, "startTime": time, "theater": theatre,
                      "title": title, "year": year, "nbrOfTickets": tickets_taken})
    response.status = 200
    return format_response({"data": total})


run(host=HOST, port=PORT, debug=True)
