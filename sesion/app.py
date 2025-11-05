from flask import Flask, render_template, request, redirect, url_for, session
import time

app = Flask(__name__)
app.secret_key = 'clave_secreta'

USUARIO_VALIDO = 'pilar'
PASSWORD_VALIDO = '123'

TIEMPO_BLOQUEO = 15  # bloqueo temporal (segundos)

@app.route('/')
def index():
    if 'intentos' not in session:
        session['intentos'] = 0
    if 'bloqueado_hasta' in session and time.time() < session['bloqueado_hasta']:
        return redirect(url_for('error'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario'].strip().lower()
    password = request.form['password']

    # Verifica bloqueo
    if 'bloqueado_hasta' in session and time.time() < session['bloqueado_hasta']:
        return redirect(url_for('error'))

    if usuario == USUARIO_VALIDO and password == PASSWORD_VALIDO:
        session['usuario'] = usuario
        session['intentos'] = 0
        return redirect(url_for('dashboard'))
    else:
        session['intentos'] = session.get('intentos', 0) + 1
        intentos_restantes = 3 - session['intentos']

        if intentos_restantes > 0:
            return render_template('index.html', error=f"Te queda {intentos_restantes} intento{'s' if intentos_restantes > 1 else ''}.")
        else:
            session['bloqueado_hasta'] = time.time() + TIEMPO_BLOQUEO
            session['intentos'] = 0
            return render_template('index.html', error="Se acabaron tus intentos, vuelve a intentar.")

@app.route('/dashboard')
def dashboard():
    if 'usuario' in session:
        return render_template('dashboard.html', usuario=session['usuario'])
    return redirect(url_for('index'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('usuario', None)
    session['intentos'] = 0
    return redirect(url_for('index'))

@app.route('/error')
def error():
    restante = 0
    if 'bloqueado_hasta' in session:
        restante = int(session['bloqueado_hasta'] - time.time())
        if restante < 0:
            restante = 0
    return render_template('error.html', tiempo_restante=restante)

if __name__ == '__main__':
    app.run(debug=True)
