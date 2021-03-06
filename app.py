import functools
from flask import Flask, render_template, request, flash, redirect, url_for, g, session, make_response
from db import get_db

from werkzeug.security import generate_password_hash, check_password_hash

import os
import utils

app = Flask(__name__)
app.secret_key = os.urandom(12)


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
        g.user = db.execute('SELECT * FROM usuarios WHERE id_usuario = ?', (user_id,)).fetchone()


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

            user = db.execute('SELECT * FROM usuarios WHERE usuario = ?',
                              (username,)).fetchone()

            if user is None:
                error = 'Usuario o contraseña inválidos'
            else:
                id_tipo_usuario = user[1]
                store_password = user[5]
                result = check_password_hash(store_password, password)
                if result is True and id_tipo_usuario == 1:
                    session.clear()
                    session['user_id'] = user[0]
                    resp = make_response(redirect(url_for('home')))
                    resp.set_cookie('username', username)
                    return resp
                if result is True and id_tipo_usuario == 2:
                    session.clear()
                    session['user_id'] = user[0]
                    resp = make_response(redirect(url_for('home')))
                    resp.set_cookie('username', username)
                    return resp
                if result is True and id_tipo_usuario == 3:
                    session.clear()
                    session['user_id'] = user[0]
                    resp = make_response(redirect(url_for('home')))
                    resp.set_cookie('username', username)
                    return resp

                else:
                    error = 'Usuario o contraseña inválidos'
            flash(error)
        return render_template('login.html')
    except Exception as ex:
        print(ex)
        return render_template('login.html')


@app.route('/users', methods=('GET', 'POST'))
@login_required
def view_users():
    db = get_db()
    users = db.execute('SELECT * FROM usuarios').fetchall()
    return render_template("users.html", users=users)


@app.route('/user/<int:user_id>')
@login_required
def view_user(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM usuarios WHERE id_usuario= ?', (user_id,)).fetchone()
    if user:
        return render_template('user.html', user=user)
    return f"Usuario con id ={user_id} no existe"


@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id', 'user_id')
    db = get_db()
    user = db.execute('SELECT * FROM usuarios WHERE id_usuario= ?', (user_id,)).fetchone()
    if user:
        return render_template('profile.html', user=user)
    return f"Usuario con id ={user_id} no existe"


@app.route('/search-flights', methods=('GET', 'POST'))
@login_required
def search_flights():
    try:
        # Si el metodo de request es POST
        if request.method == 'POST':
            departure_date = request.form['departure_date']
            return_date = request.form['return_date']
            origin = request.form['origin']
            destiny = request.form['destiny']
            passengers = request.form['passengers']
            db = get_db()
            flights = db.execute(
                'SELECT * FROM vuelos WHERE fecha_salida=? and fecha_regreso=? and origen=? and destino=?',
                (departure_date, return_date, origin, destiny)).fetchall()

            if not flights:
                error = 'No se encontraron vuelos'
                return render_template("flights.html", error=error)

            return render_template("flights.html", flights=flights)
        return render_template("search_flights.html")
    except Exception as e:
        print(e)
        return 'error'


@app.route('/flights', methods=('GET', 'POST'))
@login_required
def view_flights():
    db = get_db()
    flights = db.execute('SELECT * FROM vuelos').fetchall()
    return render_template("flights.html", flights=flights)


@app.route('/flight/<int:id_de_vuelo>')
@login_required
def view_flight(id_de_vuelo):
    db = get_db()
    id_de_vuelo = db.execute('SELECT * FROM vuelos WHERE id_de_vuelo= ?', (id_de_vuelo,)).fetchone()
    if id_de_vuelo:
        return render_template('flight.html', flight=id_de_vuelo)
    return f"Vuelo con id ={id_de_vuelo} no existe"


@app.route('/book-flight/<int:id_de_vuelo>', methods=('GET', 'POST'))
@login_required
def book_flight(id_de_vuelo):
    try:
        user_id = session.get('user_id', 'user_id')
        id_vuelo = id_de_vuelo
        print(id_vuelo)
        if request.method == 'POST':
            db = get_db()
            vuelo = db.execute('SELECT * FROM vuelos WHERE id_de_vuelo= ?', (id_vuelo,)).fetchone()
            print(vuelo)
            user = db.execute('SELECT * FROM usuarios WHERE id_usuario= ?', (user_id,)).fetchone()
            birthday = request.form['birthday']
            doc_user = request.form['doc_user']

            db.execute(
                'INSERT INTO reserva (id_usuario, id_de_vuelo, origen, destino, fecha_salida, hora_salida,fecha_regreso,hora_regreso) VALUES (?,?,?,?,?,?,?,?)',
                (user_id, vuelo[0], vuelo[4], vuelo[5], vuelo[7], vuelo[8], vuelo[9], vuelo[10]))
            print('ok')
            db.execute('UPDATE usuarios SET fecha_nacimiento=?, documento_usuario=?  WHERE id_usuario=?',
                       (birthday, doc_user, user_id))
            print('ok')
            db.commit()

            return render_template('thanks.html', name=user[2])
        return render_template('confirmation.html', user_id=user_id, id_vuelo=id_vuelo)
    except Exception as e:
        print(e)
        return render_template('home.html')


@app.route('/pilots', methods=('GET', 'POST'))
@login_required
def view_pilots():
    db = get_db()
    pilots = db.execute('SELECT * FROM pilotos').fetchall()
    return render_template("pilots.html", pilots=pilots)


@app.route('/pilot/<int:id_piloto>')
@login_required
def view_pilot(id_piloto):
    db = get_db()
    id_piloto = db.execute('SELECT * FROM pilotos WHERE id_piloto= ?', (id_piloto,)).fetchone()
    if id_piloto:
        return render_template('pilot.html', pilot=id_piloto)
    return f"Piloto con id ={id_piloto} no existe"


@app.route('/bookings', methods=('GET', 'POST'))
@login_required
def view_bookings():
    db = get_db()
    bookings = db.execute('SELECT * FROM reserva').fetchall()
    return render_template("bookings.html", bookings=bookings)


@app.route('/booking/<int:id_reserva>')
@login_required
def view_booking(id_reserva):
    db = get_db()
    id_reserva = db.execute('SELECT * FROM reserva WHERE id_reserva= ?', (id_reserva,)).fetchone()
    if id_reserva:
        return render_template('booking.html', booking=id_reserva)
    return f"Reserva con id ={id_reserva} no existe"


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

            # generate_password_hash

            # verificamos si el correo ya existe en la base de datos

            user = db.execute('SELECT id_usuario FROM usuarios WHERE correo=?', (email,)).fetchone()

            # Si el correo existe entonces lanza un error y direcciona a registro
            if user is not None:
                error = 'el correo ya existe'.format(email)
                flash(error)
                return render_template('register.html')

            db.execute('INSERT INTO usuarios (id_tipo_usuario,nombre, usuario, correo, contraseña) VALUES (?,?,?,?,?)',
                       (3, name, username, email, generate_password_hash(password)))

            db.commit()
            # db.close()

            # yag = yagmail.SMTP('mintic202221@gmail.com','Mintic2022')
            # yag.send(to=email, subject= 'Activa tu cuenta',
            #          contents='Bievenido al portal gestion de vuelos para el aeropuerto perales '
            #                   'para activar tu cuenta')
            #
            # flash("Revisa tu correo para activar tu cuenta")
            # return render_template('register.html')

            return render_template('login.html')
        return render_template('register.html')
    except Exception as e:
        print(e)
        return render_template('register.html')


@login_required
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/home', methods=('GET', 'POST'))
@login_required
def home():
    try:
        username = request.cookies.get('username')
        user_id = session.get('user_id')
        db = get_db()
        user = db.execute('SELECT * FROM usuarios WHERE id_usuario = ?', (user_id,)).fetchone()

        return render_template('home.html', username=username, tipo_usuario=user[1])
    except Exception as e:
        print(e)


@app.route('/editbooking/<int:id_booking>', methods=('GET', 'POST'))
def edit_booking(id_booking):
    db = get_db()
    booking = db.execute('SELECT * FROM reserva WHERE id_reserva= ?', (id_booking,)).fetchone()
    if booking:
        return render_template('edit_booking.html', booking=booking)
    return f"Reserva con id ={id_booking} no existe"


if __name__ == '__main__':
    app.run()
