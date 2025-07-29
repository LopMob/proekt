from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret-key'
DB_PATH = 'db.sqlite3'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Хранилище лотов (динамические + статические)
static_lots = [
    {"id": 1, "title": "Tesla Model S", "year": 2022, "engine": "Dual Motor 100 kWh", "hp": 762, "color": "Чёрный", "price": "3 000 000 ₽", "img": "tesla.jpg"},
    {"id": 2, "title": "BMW M5", "year": 2020, "engine": "4.4L V8", "hp": 600, "color": "Синий", "price": "4 500 000 ₽", "img": "bmw.jpg"},
    {"id": 3, "title": "Lada Aura", "year": 2022, "engine": "1.6 turbo", "hp": 230, "color": "Зелёный", "price": "1 500 000 ₽", "img": "lada.jpg"},
]
dynamic_lots = []

# --- DB INIT ---
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')
        conn.commit()


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        with sqlite3.connect(DB_PATH) as conn:
            try:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))
                conn.commit()
                return redirect(url_for('login'))
            except:
                return "Пользователь уже существует"
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
            if c.fetchone():
                session['user'] = user
                return redirect(url_for('auction'))
            else:
                return "Неверные данные"
    return render_template('login.html')


@app.route('/auction')
def auction():
    if 'user' not in session:
        return redirect(url_for('login'))

    combined_lots = static_lots + [
        {**lot, "id": len(static_lots) + i + 1} for i, lot in enumerate(dynamic_lots)
    ]

    news_list = [
        {"id": 1, "title": "Новый электрокар Tesla", "date": "2025-07-01"},
        {"id": 2, "title": "Снижение цен на BMW", "date": "2025-07-15"},
        {"id": 3, "title": "Новые правила ОСАГО", "date": "2025-07-20"},
    ]
    return render_template('auction.html', news=news_list, lots=combined_lots)


@app.route('/news/<int:news_id>')
def news_detail(news_id):
    news_data = {
        1: {
            "title": "Новый электрокар Tesla",
            "content": "Tesla выпустила новый электромобиль с запасом хода более 800 км...",
            "date": "2025-07-01",
            "img": "news1.jpg"
        },
        2: {
            "title": "Снижение цен на BMW",
            "content": "BMW снизила цены на модели M-серии...",
            "date": "2025-07-15",
            "img": "news2.jpg"
        },
        3: {
            "title": "Новые правила ОСАГО",
            "content": "С 1 августа вступают в силу новые правила расчета стоимости ОСАГО...",
            "date": "2025-07-20",
            "img": "news3.jpg"
        }
    }
    news = news_data.get(news_id)
    if not news:
        return "Новость не найдена"
    return render_template('news_detail.html', news=news)


@app.route('/lot/<int:lot_id>')
def lot_detail(lot_id):
    all_lots = static_lots + dynamic_lots
    if 1 <= lot_id <= len(all_lots):
        lot = all_lots[lot_id - 1]
        return render_template('lot_detail.html', lot=lot)
    return "Лот не найден"


@app.route('/add_lot', methods=['GET', 'POST'])
def add_lot():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        year = int(request.form['year'])
        engine = request.form['engine']
        hp = int(request.form['hp'])
        color = request.form['color']
        price = request.form['price']

        # обработка изображения
        file = request.files['img']
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        else:
            filename = "default.jpg"

        new_lot = {
            "title": title,
            "year": year,
            "engine": engine,
            "hp": hp,
            "color": color,
            "price": price,
            "img": f"uploads/{filename}"
        }
        dynamic_lots.append(new_lot)
        return redirect(url_for('auction'))

    return render_template('add_lot.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
