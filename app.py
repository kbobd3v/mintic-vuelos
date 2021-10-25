import functools
from flask import Flask, render_template, request, flash, redirect, url_for, g, session, make_response
from db import get_db

from werkzeug.security import generate_password_hash, check_password_hash

import os
import utils

app = Flask(__name__)
app.secret_key = os.urandom(12)


@app.route("/")
def index():
    # Render_template te permite visualizar un html con la información que requieres
    # Puedes pasar parametros a la url para que sean tenidos en cuenta dentro del html
    if g.user:
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route("/login", methods=('GET', 'POST'))
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Siempre abrir la conexion
            db = get_db()
            error = None

            if not username:
                error = 'Debes ingresar un usuario'
                flash(error)
                return render_template('login.html')

            if not password:
                error = 'Debes ingresar una contraseña'
                flash(error)
                return render_template('login.html')

            user = db.execute('SELECT * FROM usuario WHERE usuario = ?',
                              (username, )).fetchone()

            if user is None:
                error = 'Usuario o contraseña invalidos'
                flash(error)
            else:
                store_password = user[4]
                result = check_password_hash(store_password, password)
                if result is False:
                    error = 'Usuario o contraseña invalidos'
                else:
                    session.clear()
                    session['user_id'] = user[0]
                    resp = make_response(redirect(url_for('home')))
                    resp.set_cookie('username', username)
                    return resp
            flash(error)
        return render_template('login.html')
    except Exception as ex:
        print(ex)
        return render_template('login.html')


@app.route('/register', methods=('GET', 'POST'))
def register():
    try:
        # Si el metodo de request es POST
        if request.method == 'POST':
            name = request.form['name']
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            if not utils.isEmailValid(email):
                error = "El email no es valido"
                flash(error)
                return render_template('register.html')

            if not utils.isUsernameValid(username):
                error = "El usuario no es valido"
                flash(error)
                return render_template('register.html')

            if not utils.isPasswordValid(password):
                error = "El password no es valido"
                flash(error)
                return render_template('register.html')

            db = get_db()

            #generate_password_hash

            #verificamos si el correo ya existe en la base de datos

            user = db.execute('SELECT id_usuario FROM usuario WHERE correo=?', (email,)).fetchone()

            # Si el correo existe entonces lanza un error y direcciona a registro
            if user is not None:
                error = 'el correo ya existe'.format(email)
                flash(error)
                return render_template('register.html')

            db.executescript('INSERT INTO usuario (nombre, usuario, correo, contraseña) VALUES ("%s","%s","%s","%s")' %
                             (name, username, email, generate_password_hash(password)))

            db.commit()
            # db.close()

            # yag = yagmail.SMTP('mintic202221@gmail.com','Mintic2022')
            # yag.send(to=email, subject= 'Activa tu cuenta',
            #          contents='Bievenido al portal de Registro de Vacunación  usa este link '
            #                   'para activar tu cuenta')
            #
            # flash("Revisa tu correo para activar tu cuenta")
            # return render_template('register.html')

            return render_template('login.html')
        return render_template('register.html')
    except Exception as e:
        print(e)
        return render_template('register.html')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute('SELECT * FROM usuario WHERE id_usuario = ?', (user_id, )).fetchone()


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/home', methods=('GET', 'POST'))
@login_required
def home():
    try:
        return render_template('home.html')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run()
