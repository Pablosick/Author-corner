from flask import Flask, render_template, url_for, request, flash, session, redirect, abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zlGK5teFsXX4e3jfyO'

menu = [{"name": "Главная", "url": "/"},
        {"name": "Статьи", "url": "article-flask"},
        {"name": "Обратная связь", "url": "contact"}
]

reg_a_log = [{"name": "Вход", "url": "entry-preson"},
             {"name": "Авторизация", "url": "login"}
]


@app.route('/')
def index():
    return render_template('index.html', title='Backend на Flask', menu=menu, login=reg_a_log)


@app.route('/contact', methods=["POST", "GET"]) #Если не указать метод POST, то на кнопку отправить будет ошибка 405. Сервер получает запрос, но не может его реализовать
def contact():
    if request.method == "POST":
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')

    return render_template('contact.html', title='Обратная связь', menu=menu, login=reg_a_log)


@app.route('/login', methods=["POST", "GET"])
def login():
    if 'user' in session:
        return redirect(url_for('profile', username=session['user']))
    elif request.method == 'POST' and request.form['username'] == 'test' and request.form['psw'] == "123":
        session['user'] = request.form['username']  # connect session
        return redirect(url_for('profile', username=session['user']))
    return render_template('login.html', title='Авторизация', menu=menu, login=reg_a_log)


@app.route('/profile/<username>')
def profile(username):
    if 'user' not in session or session['user'] != username:
        abort(401)  # Unauthorized  user (Прерывание запроса)
    return render_template('profile.html', title=f'Профиль пользователя {username}', menu=menu, login=reg_a_log)

@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu, login=reg_a_log)


if __name__ == "__main__":
    app.run(debug=True)









