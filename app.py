import os.path
import sqlite3 as sq
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    flash,
    session,
    redirect,
    abort,
    g,
)
from DatabaseMainMenu import FDatabase


# Configuration WSGI-application

DATABASE = os.getenv("DATABASE")
DEBUG = os.getenv("DEBUG")
SECRET_KEY = os.getenv("SECRET_KEY")


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, "fslite.db")))


def connect_db():
    conn = sq.connect(app.config["DATABASE"])
    conn.row_factory = sq.Row
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource("sq_db.sql", mode="r") as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Соединение с БД, если оно еще не установлено"""
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()
    return g.link_db


menu = [
    {"name": "Главная", "url": "/"},
    {"name": "Статьи", "url": "/article-flask"},
    {"name": "Обратная связь", "url": "/contact"},
]

reg_a_log = [
    {"name": "Вход", "url": "/entry-preson"},
    {"name": "Авторизация", "url": "/login"},
]


@app.route("/")
def index():
    print(request.form)
    db = get_db()
    database = FDatabase(db)
    return render_template(
        "index.html", title="Backend на Flask", menu=database.getMenu(), login=reg_a_log
    )


@app.route("/article-flask", methods=["POST", "GET"])
def articleFlask():
    db = get_db()
    database = FDatabase(db)

    if request.method == "POST":
        if len(request.form["name"]) > 4 and len(request.form["post"]) > 10:
            res = database.addPost(request.form["name"], request.form["post"])
            if not res:
                flash("Ошибка добавления статьи", category="error")
            else:
                flash("Статья добавлена успешно", category="success")
        else:
            flash("Ошибка добавления статьи", category="error")

    return render_template(
        "add_post.html",
        title="Добавление статьи",
        menu=database.getMenu(),
        login=reg_a_log,
    )


@app.route(
    "/contact", methods=["POST", "GET"]
)  # Если не указать метод POST, то на кнопку отправить будет ошибка 405. Сервер получает запрос, но не может его реализовать
def contact():
    db = get_db()
    database = FDatabase(db)
    if request.method == "POST":
        if len(request.form["username"]) > 2:
            flash("Сообщение отправлено", category="success")
        else:
            flash("Ошибка отправки", category="error")

    return render_template(
        "contact.html", title="Обратная связь", menu=database.getMenu(), login=reg_a_log
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    db = get_db()
    database = FDatabase(db)
    if "user" in session:
        return redirect(url_for("profile", username=session["user"]))
    elif (
        request.method == "POST"
        and request.form["username"] == "test"
        and request.form["psw"] == "123"
    ):
        session["user"] = request.form["username"]  # connect session
        return redirect(url_for("profile", username=session["user"]))
    return render_template(
        "login.html", title="Авторизация", menu=database.getMenu(), login=reg_a_log
    )


@app.route("/profile/<username>")
def profile(username):
    db = get_db()
    database = FDatabase(db)
    if "user" not in session or session["user"] != username:
        abort(401)  # Unauthorized  user (Прерывание запроса)
    return render_template(
        "profile.html",
        title=f"Профиль пользователя {username}",
        menu=database.getMenu(),
        login=reg_a_log,
    )


@app.errorhandler(404)
def pageNotFount(error):
    db = get_db()
    database = FDatabase(db)
    return render_template(
        "page404.html",
        title="Страница не найдена",
        menu=database.getMenu(),
        login=reg_a_log,
    )


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установленно"""
    if hasattr(g, "link_db"):
        g.link_db.close()


if __name__ == "__main__":
    app.run(debug=True)

