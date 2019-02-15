from bottle import get, post, run, request, response
import sqlite3
import json
import os

from hashlib import sha256

HOST = 'localhost'
PORT = 4568

schema_path = os.path.abspath('schemas')
print(schema_path)

conn = sqlite3.connect("applications.sqlite")


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
    return "pong"

@post('/reset')
def reset():
    def _hash(pwd: str) -> str:
        sh = sha256()
        sh.update(pwd.encode(encoding='utf-8'))
        return sh.hexdigest()
    cursor = conn.cursor()
    with open(f'{schema_path}/reset.sql', 'r') as f:
        sqls = f.read()
    conn.executescript(sqls)

    users = [('alice', 'Alice', 'dobido'),
             ('bob', 'Bob', 'whatsinaname')]
    for uname, name, plainpwd in users:
        command = f"INSERT INTO customers(username, name, pwd) values('{uname}', '{name}', '{_hash(plainpwd)}')"
        print("Executing {}".format(command))
        cursor.execute(command)
    conn.commit()
    # TODO! reset database!
    response.status = 200
    return "OK"

@post('/students')
def post_student():
    response.content_type = 'application/json'
    name = request.query.name
    gpa = request.query.gpa
    hsSize = request.query.hsSize
    if not (name and gpa and hsSize):
        response.status = 400
        return format_response({"error": "Missing parameter"})
    c = conn.cursor()
    c.execute(
        """
        INSERT
        INTO   students(s_name, gpa, size_hs)
        VALUES (?, ?, ?)
        """,
        [name, gpa, hsSize]
    )
    conn.commit()
    c.execute(
        """
        SELECT   s_id
        FROM     students
        WHERE    rowid = last_insert_rowid()
        """
    )
    id = c.fetchone()[0]
    response.status = 200
    return format_response({"id": id, "url": url(f"/students/{id}")})


run(host=HOST, port=PORT, debug=True)