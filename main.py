import os
import sqlite3

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

DATABASE = "/tmp/flask-app.db"
DEBUG = True
SECRET_KEY = "ajsgbashsabiur345j3h4g"

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "flask-app.db")))


def connect_db():
    """Создание БД."""
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД."""
    db = connect_db()
    with app.open_resource("sq_db.sql", mode="r") as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Соединение с БД, если оно еще не установлено."""
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установлено."""
    if hasattr(g, "link_db"):
        g.link_db.close()


menu = [
    {"name": "Установка", "url": "install-flask"},
    {"name": "Первое приложение", "url": "first-app"},
    {"name": "Обратная связь", "url": "contact"},
]


# @app.route("/")
# def index():
#     return render_template("index.html", menu=menu)


@app.route("/")
def index():
    db = get_db()
    return render_template("index.html", menu=[])


@app.route("/about")
def about():
    return render_template("about.html", title="О нашем сайте", menu=menu)


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        if len(request.form["username"]) > 2:
            flash("Сообщение отправлено!", category="success")
        else:
            flash("Ошибка отправки", category="error")
    return render_template("contact.html", title="Обратная связь", menu=menu)


@app.errorhandler(404)
def page_not_found(error):
    return (
        render_template(
            "page404.html", title="Страница не найдена", menu=menu
        ),
        404,
    )


@app.route("/profile/<username>")
def profile(username):
    if "userLogged" not in session or session["userLogged"] != username:
        abort(401)
    return f"Профиль пользователя: {username}"


@app.route("/login", methods=["POST", "GET"])
def login():
    if "userLogged" in session:
        return redirect(url_for("profile", username=session["userLogged"]))
    elif (
        request.method == "POST"
        and request.form["username"] == "alex"
        and request.form["psw"] == "123"
    ):
        session["userLogged"] = request.form["username"]
        return redirect(url_for("profile", username=session["userLogged"]))
    return render_template("login.html", title="Авторизация", menu=menu)


if __name__ == "__main__":
    app.run(debug=True)
