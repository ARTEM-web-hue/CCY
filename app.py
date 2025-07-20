from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Путь к БД
DATABASE = 'database.db'

# Проверка токена (пример)
VALID_TOKEN = "admin123"

# Создание таблицы
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

# Получение БД
def get_db():
    return sqlite3.connect(DATABASE)

@app.route('/admin-panel-innd', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username')
        image_url = request.form.get('image_url')
        size = request.form.get('size')

        if username and image_url and size:
            db = get_db()
            db.execute('INSERT INTO trophies (username, image_url, size) VALUES (?, ?, ?)',
                       (username, image_url, size))
            db.commit()
            flash("Трофей добавлен!")
            return redirect(url_for('admin'))

    db = get_db()
    trophies = db.execute('SELECT username, image_url, size FROM trophies').fetchall()
    return render_template('admin.html', trophies=trophies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = request.form.get('token')
        if token == VALID_TOKEN:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash("Неверный токен!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
