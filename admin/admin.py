import sqlite3

from flask import Blueprint, request, flash, render_template, redirect, url_for, session, g
from src.model.Database import db, Users, Posts

admin = Blueprint("admin", __name__, template_folder="templates", static_folder="static")


def login_admin():
    session['admin_logged'] = 1


def is_logged():
    return True if session.get("admin_logged") else False


def logout_admin():
    session.pop("admin_logged", None)


@admin.route("/")
def index():
    if not is_logged():
        return redirect(url_for(".login"))

    return render_template(
        "admin/index.html",
        title="Админ-панель",
        menu=True
    )


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

    return render_template(
        "admin/login.html",
        title="Админ-панель"
    )


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
    article_list = None
    try:
        article_list = Posts.query.all()
    except Exception as e:
        print(f"Ошибка получения статей из БД: {e}")

    return render_template(
        "admin/listpubs.html",
        title="Список статей",
        list=article_list, menu=True
    )


@admin.route("/list-users")
def list_users():
    if not is_logged():
        return redirect(url_for(".login"))
    users_list = None
    try:
        users_list = Users.query.all()
    except sqlite3.Error as e:
        print(f"Ошибка получения пользователей: {e}")

    return render_template(
        "admin/listusers.html",
        title="Список пользователей",
        list=users_list, menu=True)


@admin.route("/list-users/<id>")
def user_posts(id):
    if not is_logged():
        return redirect(url_for(".login"))
    user_post = None
    try:
        user_post = db.session.query(Users, Posts).join(Posts, Users.id == Posts.user_id).filter(Users.id == id).all()
    except Exception as e:
        print(f"Ошибка получения статей пользователей: {e}")
    name = user_post[0].Users.name if user_post else Users.query.filter_by(id=id).first().name
    return render_template(
        "admin/list_user_posts.html",
        title=f"Список статей пользователя: {name}",
        list_user_posts=user_post,
        menu=True
    )
