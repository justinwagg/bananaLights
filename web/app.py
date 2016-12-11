#!/usr/bin/python

from flask import Flask, render_template, request, g
import sqlite3
import itertools
import flask_table
from flask_table import Table, Col




DATABASE = '/home/pi/Documents/bananaLights/database/settings.db'


class ItemTable(Table):
    rest = Col('rest')
    high = Col('high')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def getAll():
	q = """
		select 'daytime' as mode, rest, high from mode0 where rowid = (select max(rowid) from mode0)
		UNION
		select 'evening' as mode, rest, high from mode1 where rowid = (select max(rowid) from mode1)
		UNION
		select 'overnight' as mode, rest, high from mode2 where rowid = (select max(rowid) from mode2)
		UNION
		select 'manual' as mode, rest, high from mode3 where rowid = (select max(rowid) from mode3)
		;
		"""
	cur = get_db().execute(q)
	results = cur.fetchall()
	cur.close()
	return results

def hours():
	q = "select h1, h2, h3 from hours where rowid = (select max(rowid) from hours);"
	cur = get_db().execute(q)
	results = cur.fetchall()
	cur.close()
	return results

app = Flask(__name__)
app.secret_key = 'SHH!'

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def main():
	x = result2()
	return render_template('index.html', test = x)

@app.route('/list')
def list():

	x = getAll()
	y = hours()
	return render_template("list.html", rows = x, hour = y)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)    







