import os.path
from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from src.model.UserLogin import UserLogin
from src.model.Database import db, Users, Posts
from src.model.forms import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from admin.admin import admin
from uuid import uuid4

# Configuration WSGI-application

DATABASE = os.getenv("DATABASE")
DEBUG = os.getenv("DEBUG")
SECRET_KEY = os.getenv("SECRET_KEY")

# Max content length
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)

# Secret-key for session
app.config['SECRET_KEY'] = str(uuid4())
app.config.update(dict(DATABASE=os.path.join(app.root_path, "fslite.db")))

# Register blueprint
app.register_blueprint(admin, url_prefix="/admin")

# Login-manager and his config
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Требуется авторизоваться для доступа к закрытым страницам'
login_manager.login_message_category = 'error'

# Conf SqlAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///article.db"
db.init_app(app)
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    print("load user")
    return UserLogin().from_db(user_id, user=Users)


@app.route("/")
def index():
    posts = Posts.query.all()
    return render_template(
        "index.html",
        title="Список статей",
        posts=posts
    )


@app.route("/article-flask", methods=["POST", "GET"])
@login_required
def articleFlask():
    if request.method == "POST":
        if len(request.form["name"]) > 4 and len(request.form["post"]) > 10:
            try:
                post = Posts(title=request.form['name'],
                             text=request.form['post'],
                             url=request.form['url'],
                             user_id=int(current_user.get_id()))
                db.session.add(post)
                db.session.commit()
                flash("Статья добавлена успешно", category="success")
            except Exception as e:
                db.session.rollback()
                print("Ошибка чтения из БД: ", e)
                flash("Ошибка добавления статьи", category="error")
        else:
            flash("Ошибка добавления статьи", category="error")

    return render_template(
        "add_post.html",
        title="Добавление статьи",
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("profile_users"))

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.psw, form.psw.data):
            user_login = UserLogin().create(user)
            rem_me = form.remember.data
            login_user(user_login, remember=rem_me)
            return redirect(request.args.get("next") or url_for('profile_users'))

        flash("Неверная пара логин/пароль", "error")
    return render_template(
        "login.html",
        title="Авторизация",
        form=form
    )


@app.route("/signup", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if (len(request.form["firstname"]) > 4 and len(request.form["email"]) > 4
                and len(request.form["psw"]) > 4 and request.form["repeat_psw"] == request.form["psw"]):
            hash_psw = generate_password_hash(request.form["psw"])
            try:
                user = Users(name=request.form["firstname"],
                             email=request.form["email"],
                             psw=hash_psw)
                db.session.add(user)
                db.session.commit()
                flash("Вы успешно зарегистрированы", "success")
            except Exception as e:
                print("Ошибка добавления данных в БД", e)
                db.session.rollback()
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Ошибка введенных данных. Поля должны содержать > 4 символов", "error")
    return render_template(
        "sing_up.html",
        title="Регистрация",
    )


@app.errorhandler(404)
def pageNotFount(error):
    return render_template(
        "page404.html",
        title="Страница не найдена",
    )


@app.route("/post/<alias>")
@login_required
def show_post(alias):
    post_data = Posts.query.filter_by(url=alias).first()
    if not post_data:
        abort(401)
    return render_template(
        "post.html",
        title=post_data.title,
        post=post_data.text)


@app.route("/profile_users")
def profile_users():
    user = Users.query.filter_by(id=current_user.get_id()).first()
    return render_template(
        "profile_users.html",
        title="Профиль",
        user=user,
    )


@app.route("/ava")
@login_required
def user_ava():
    img = current_user.get_avatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers["Content-Type"] = "image/png"
    return h


@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files['file']
        print(file.filename)
        if file and current_user.check_file_png(file.filename):
            try:
                img = file.read()
                res = Users.query.filter_by(id=current_user.get_id()).first()
                res.avatar = img
                db.session.commit()
                if not res:
                    flash("Ошибка обновления аватара", "error")
                else:
                    flash("Аватар успешно загружен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения из файла")
                print(f"Ошибка чтения из файла: {e}")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for("profile_users"))


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


if __name__ == "__main__":
    app.run(debug=True)

