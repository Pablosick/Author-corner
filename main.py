from flask import Flask, render_template, url_for, request, flash, session, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zlGK5teFsXX4e3jfyO'

menu = [{"name": "Главная", "url": "main-flask"},
        {"name": "Статьи", "url": "article-flask"},
        {"name": "Обратная связь", "url": "contact"}
]

@app.route('/')
def index():
    print(url_for('index'))
    return render_template('index.html', title='Backend на Flask', menu=menu)


@app.route('/contact', methods=["POST", "GET"]) #Если не указать метод POST, то на кнопку отправить будет ошибка 405. Сервер получает запрос, но не может его реализовать
def contact():
    if request.method == "POST":
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')

    return render_template('contact.html', title='Обратная связь', menu=menu)


@app.route('/login', methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == 'selfedu' and request.form['psw'] == "123":
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html', title='Авторизация', menu=menu)


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu)

if __name__ == "__main__":
    app.run(debug=True)









