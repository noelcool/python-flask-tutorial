import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')  # blueprint named 'auth'

'''
flask will have two bludprints
ont for authentication functions and one for the blog posts functions
each blueprint will go in a separate module
'''


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username ie required'
        elif not password:
            error = 'Password is required'

        if error is None:
            try:
                q = "INSERT INTO user (username, password) VALUES(%s, %s)"
                db.execute(q, (username, generate_password_hash(password)))
                db.connection.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        q = "SELECT * FROM user WHERE username = %s"
        db.execute(q, (username,))
        user = db.fetchone()

        if user is None:
            error = 'Incorrect username'
        # submitted password in the same way as the stored hash and securely compares them
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request  # registers a function that runs before the view function
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        q = "SELECT * FROM user WHERE id = %s"
        db.execute(q, (user_id,))
        g.user = db.fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)  # returns a new view function that wraps the original view it's applied to
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


