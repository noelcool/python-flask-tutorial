#import sqlite3
import pymysql

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        conn = pymysql.\
            connect(host='127.0.0.1', user='root', db='python_test', password='123456', port=3307, charset='utf8')
        g.db = conn.cursor(pymysql.cursors.DictCursor)
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Init database')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)