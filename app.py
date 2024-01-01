import os.path
import sqlite3 as sq
from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g
from werkzeug.security import generate_password_hash, check_password_hash
from DatabaseMainMenu import FDatabase
from UserLogin import UserLogin

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from uuid import uuid4

# Configuration WSGI-application

DATABASE = os.getenv("DATABASE")
DEBUG = os.getenv("DEBUG")
SECRET_KEY = os.getenv("SECRET_KEY")


app = Flask(__name__)
app.config.from_object(__name__)

# Secret-key for session
app.config['SECRET_KEY'] = str(uuid4())

app.config.update(dict(DATABASE=os.path.join(app.root_path, "fslite.db")))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Требуется авторизоваться для доступа к закрытым страницам'
login_manager.login_message_category = 'error'


@login_manager.user_loader
def load_user(user_id):
    print("load user")
    return UserLogin().from_db(user_id, g.database)


def connect_db():
    conn = sq.connect(app.config["DATABASE"])
    conn.row_factory = sq.Row
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД. Чтение SQL запросов из файла"""
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


@app.before_request
def accessing_the_database():
    g.db = get_db()
    g.database = FDatabase(g.db)


@app.route("/")
def index():
    return render_template(
        "index.html", title="Список статей",
        menu=g.database.get_menu([1, 2]),
        login=g.database.get_menu([3, 4]),
        logout=g.database.get_menu([5, 6]),
        posts=g.database.get_all_post()
    )


@app.route("/article-flask", methods=["POST", "GET"])
def articleFlask():
    if request.method == "POST":
        if len(request.form["name"]) > 4 and len(request.form["post"]) > 10:
            res = g.database.add_post(request.form["name"], request.form["post"], request.form["url"])
            if not res:
                flash("Ошибка добавления статьи", category="error")
            else:
                flash("Статья добавлена успешно", category="success")
        else:
            flash("Ошибка добавления статьи", category="error")

    return render_template(
        "add_post.html",
        title="Добавление статьи",
        menu=g.database.get_menu([1, 2]),
        login=g.database.get_menu([3, 4]),
        logout=g.database.get_menu([5, 6]),
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("profile_users"))

    if request.method == "POST":
        user = g.database.get_user_by_email(request.form['username'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            user_login = UserLogin().create(user)
            rem_me = True if request.form.get('rememberme') else False
            login_user(user_login, remember=rem_me)
            return redirect(request.args.get("next") or url_for('profile_users'))

        flash("Неверная пара логин/пароль", "error")
    return render_template(
        "login.html",
        title="Авторизация",
        menu=g.database.get_menu([1, 2]),
        login=g.database.get_menu([3, 4]),
        logout=g.database.get_menu([5, 6]),
    )


@app.route("/signup", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if (len(request.form["firstname"]) > 4 and len(request.form["email"]) > 4
                and len(request.form["psw"]) > 4 and request.form["repeat_psw"] == request.form["psw"]):
            hash_psw = generate_password_hash(request.form["psw"])
            res = g.database.user_registration(request.form["firstname"], request.form["email"], hash_psw)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for("login"))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Ошибка введенных данных", "error")
    return render_template(
        "sing_up.html",
        title="Регистрация",
        menu=g.database.get_menu([1, 2]),
        login=g.database.get_menu([3, 4]),
        logout=g.database.get_menu([5, 6]),
    )


@app.route("/profile/<username>")
def profile(username):
    if "userLogged" not in session or session["userLogged"] != username:
        abort(401)  # Unauthorized  user (Прерывание запроса)
    return render_template(
        "profile.html",
        title=f"Профиль пользователя {username}",
        menu=g.database.get_menu([1, 2]),
        login=g.database.get_menu([3, 4]),
        logout=g.database.get_menu([5, 6]),
    )


@app.errorhandler(404)
def pageNotFount(error):
    return render_template(
        "page404.html",
        title="Страница не найдена",
        menu=g.database.get_menu([1, 2]),
        login=g.database.get_menu([3, 4]),
        logout=g.database.get_menu([5, 6]),
    )


@app.route("/post/<alias>")
@login_required
def show_post(alias):
    title, post = g.database.get_post(alias)
    if not post:
        abort(401)
    return render_template(
        "post.html",
        title=title,
        menu=g.database.get_menu([1, 2]),
        login=g.database.get_menu([3, 4]),
        logout=g.database.get_menu([5, 6]),
        post=post)


@app.route("/profile_users")
def profile_users():
    return render_template(
        "profile_users.html",
        title="Профиль",
        user=g.database.get_user(current_user.get_id()),
        menu=g.database.get_menu([1, 2]),
        login=g.database.get_menu([3, 4]),
        logout=g.database.get_menu([5, 6])
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for("login"))


@app.route("/session")
def session_obj():
    data = [1, 2, 3, 4]
    session.permanent = True
    if 'data' not in session:
        session['data'] = data
    else:
        session['data'][-1] += 1
        session.modified = True   # Свойство для принудительной передачи объекта session (вне зависимости изменяемости)

    return f"<p>session['data'] = {session['data']}"


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установленно"""
    if hasattr(g, "link_db"):
        g.link_db.close()


if __name__ == "__main__":
    app.run(debug=True)

