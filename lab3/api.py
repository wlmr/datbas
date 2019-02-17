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


def _hash(text: str) -> str:
    sh = sha256()
    sh.update(text.encode(encoding='utf-8'))
    val = sh.hexdigest()
    logger.debug(f"plaintext \"{text}\" hashed into \"{val}\"")
    return val


def _sanitize(text: str) -> str:
    return text.replace("'", "''")


def url(resource):
    return f"http://{HOST}:{PORT}{resource}"


def format_response(d):
    return json.dumps(d, indent=4) + "\n"


@get('/students')
def get_students():
    response.content_type = 'application/json'
    query = """
        SELECT s_id, s_name, gpa, size_hs
        FROM   students
        WHERE  1 = 1
        """
    params = []
    if request.query.name:
        query += "AND s_name = ?"
        params.append(request.query.name)
    if request.query.minGPA:
        query += "AND gpa >= ?"
        params.append(request.query.minGPA)
    c = conn.cursor()
    c.execute(
        query,
        params
    )
    s = [{"id": id, "name": name, "gpa": gpa, "hsSize": hs_size}
         for (id, name, gpa, hs_size) in c]
    response.status = 200
    return format_response({"data": s})


@get('/students/<id>')
def get_student(id):
    response.content_type = 'application/json'
    c = conn.cursor()
    c.execute(
        """
        SELECT s_id, s_name, gpa, size_hs
        FROM   students
        WHERE  s_id = ?
        """,
        [id]
    )
    s = [{"id": id, "name": name, "gpa": gpa, "hsSize": hs_size}
         for (id, name, gpa, hs_size) in c]
    response.status = 200
    return format_response({"data": s})


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


@post('/performances')
def add_performance():
    curs = conn.cursor()
    def _count(table, column, parameter):
        curs.execute(f"select count() from {table} where {column} = ?", [parameter])
        r = curs.fetchall()[0][0]
        return r

    #TODO
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
    unique_performance = _hash(''.join((theater,imdb, date, time)))  # simple, but it should work just fine
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








@get('/performances')
def get_performances():
    """select p.performance_id, p.start_date, p.start_time, m.title, m.year, p.theatre_name, p.seats_left
	from movies m, performances p
    where m.imdb = p.imdb
    group by p.performance_id;"""
    response.content_type = 'application/json'
    curs = conn.cursor()
    curs.execute("""
    select p.performance_id, p.start_date, p.start_time, m.title, m.year, p.theatre_name, p.seats_left
	from movies m, performances p
    where m.imdb = p.imdb
    group by p.performance_id;""")
    res = [{"performanceId": pid, "date": date, "startTime": time,
            "title": title, "year": year, "theater": theatre, "remainingSeats": seats}
           for pid, date, time, title, year, theatre, seats in curs]
    response.status = 200
    return format_response({"data": res})



# @post('/students')
# def post_student():
#     response.content_type = 'application/json'
#     name = request.query.name
#     gpa = request.query.gpa
#     hsSize = request.query.hsSize
#     if not (name and gpa and hsSize):
#         response.status = 400
#         return format_response({"error": "Missing parameter"})
#     c = conn.cursor()
#     c.execute(
#         """
#         INSERT
#         INTO   students(s_name, gpa, size_hs)
#         VALUES (?, ?, ?)
#         """,
#         [name, gpa, hsSize]
#     )
#     conn.commit()
#     c.execute(
#         """
#         SELECT   s_id
#         FROM     students
#         WHERE    rowid = last_insert_rowid()
#         """
#     )
#     id = c.fetchone()[0]
#     response.status = 200
#     return format_response({"id": id, "url": url(f"/students/{id}")})


run(host=HOST, port=PORT, debug=True)