from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Путь к БД
DATABASE = 'database.db'

# Токен админа
VALID_TOKEN = "admin123"


def init_db():
    with app.app_context():
        db = sqlite3.connect(DATABASE)
        db.execute('''
            CREATE TABLE IF NOT EXISTS trophies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                image_url TEXT NOT NULL,
                size TEXT NOT NULL
            )
        ''')
        db.commit()


def get_db():
    return sqlite3.connect(DATABASE)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token_or_username = request.form.get('token')

        # Проверяем, совпадает ли введённое значение с токеном
        if token_or_username == VALID_TOKEN:
            session['logged_in'] = True
            return redirect(url_for('admin'))

        # Или это имя пользователя?
        db = get_db()
        user_exists = db.execute(
            'SELECT 1 FROM trophies WHERE username = ?', (token_or_username,)
        ).fetchone()

        if user_exists:
            return redirect(url_for('user_trophies', username=token_or_username))

        flash("Пользователь не найден")
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/admin-panel-innd')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    db = get_db()
    trophies = db.execute('SELECT username, image_url, size FROM trophies').fetchall()
    return render_template('admin.html', trophies=trophies)


@app.route('/trophies/<username>')
def user_trophies(username):
    db = get_db()
    trophies = db.execute(
        'SELECT username, image_url, size FROM trophies WHERE username = ?', (username,)
    ).fetchall()

    if not trophies:
        return "Нет трофеев для отображения", 404

    return render_template('user_trophies.html', trophies=trophies, username=username)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
