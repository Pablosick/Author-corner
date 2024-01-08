import sqlite3

from flask import Blueprint, request, flash, render_template, redirect, url_for, session, g


admin = Blueprint("admin", __name__, template_folder="templates", static_folder="static")

menu = [{'url': '.index', 'title': 'Панель'},
        {'url': '.list_pubs', 'title': 'Список статей'},
        {'url': '.list_users', 'title': 'Список пользователей'},
        {'url': '.logout', 'title': 'Выйти'}]


def login_admin():
    session['admin_logged'] = 1


def is_logged():
    return True if session.get("admin_logged") else False


def logout_admin():
    session.pop("admin_logged", None)


@admin.before_request
def before_request():
    g.connection_db = g.get("link_db")


@admin.teardown_request
def teardown_request(error=None):
    g.connection_db = None


@admin.route("/")
def index():
    if not is_logged():
        return redirect(url_for(".login"))

    return render_template("admin/index.html", title="Админ-панель", menu=menu)


@admin.route("/login",  methods=["POST", "GET"])
def login():
    if is_logged():
        return redirect(url_for(".index"))

    if request.method == "POST":
        if request.form["user"] == "admin" and request.form["psw"] == "qwerty78":
            login_admin()
            return redirect(url_for(".index"))
        else:
            flash("Неверная пара логин/пароль")

    return render_template("admin/login.html", title="Админ-панель")


@admin.route("/logout", methods=["POST", "GET"])
def logout():
    if not is_logged():
        return redirect(".login")
    logout_admin()
    return redirect(url_for(".login"))


@admin.route("/list-pubs")
def list_pubs():
    if not is_logged():
        return redirect(url_for(".login"))
    article_list = []
    if g.connection_db:
        try:
            cur = g.connection_db.cursor()
            cur.execute("SELECT title, text, url FROM posts")
            article_list = cur.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения статей из БД: {e}")

    return render_template("admin/listpubs.html", title="Список статей", menu=menu, list=article_list)


@admin.route("/list-users")
def list_users():
    if not is_logged():
        return redirect(url_for(".login"))
    users_list = []
    if g.connection_db:
        try:
            cur = g.connection_db.cursor()
            cur.execute("SELECT name, email FROM users")
            users_list = cur.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения пользователей: {e}")

    return render_template("admin/listusers.html", title="Список пользователей", menu=menu, list=users_list)
