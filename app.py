from flask import Flask, render_template, request, flash, redirect, url_for
from db import get_db

app = Flask(__name__)


@app.route("/")
def index():
    # Render_template te permite visualizar un html con la información que requieres
    # Puedes pasar parametros a la url para que sean tenidos en cuenta dentro del html
    return redirect(url_for('login'))

@app.route('/login', methods=('GET', 'POST'))
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

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

            user = db.execute('SELECT * FROM usuario WHERE usuario= ? AND contraseña= ?', (username, password)).fetchone()

            if user is None:
                error = 'Usuario o contraseña inválidos'
                flash(error)
            else:
                return 'Login exitoso'

            db.close()

        return render_template('login.html')
    except Exception as ex:
        print(ex)
        return render_template('login.html')


if __name__ == '__main__':
    app.run()
