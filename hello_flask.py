from flask import Flask, render_template, request, session, flash, redirect
from vsearch4web import search4letters
import sqlite3 as sq
from checker import check_logged_in
import time
app = Flask(__name__)


@app.route("/login", methods=["POST", "GET"])
def do_login() -> 'html':
    if request.method == 'POST':
        login = request.form.get('email')
        password = request.form.get('psw')
        with sq.connect('users.db') as db:
            cur = db.cursor()
            cur.execute("SELECT login, password FROM users")
            if (login, password) in cur.fetchall():
                flash("You are logged in now")
                session['logged_in'] = True
                session['login'] = request.form.get('email')
            else:
                flash("Wrong login or password")
    return render_template("login.html", the_title="Авторизация")


@app.route("/register", methods=["GET", "POST"])
def register() -> 'html':
    if request.method == 'POST':
        reg = request.form.get('email')
        with sq.connect('users.db') as db:
            cur = db.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name varchar (32) not null,
                                login varchar (32) not null,
                                password varchar (32) not null
                            );""")
            cur.execute("SELECT login FROM users")
            if reg in cur.fetchall():
                flash("You already have an account", category="error")
            elif request.form['psw'] != request.form['psw2']:
                flash("Try to insert passwords again")
            elif reg not in cur.fetchall():
                do_register(request)
                flash("Your account has been created")
                session['logged_in'] = True
                session["login"] = request.form.get('email')
    return render_template("register.html", the_title="Регистрация")


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    phrase = request.form['phrase']
    letters = request.form['letters']
    title = "Here are you're results:"
    results = str(search4letters(phrase, letters))
    log_request(request, results)
    return render_template('results.html',
                           the_phrase=phrase,
                           the_letters=letters,
                           the_title=title,
                           the_results=results, )


@app.route('/')
def greating_page():
    return render_template('greating.html',
                           the_title='Welcome to search4letters on the web!')


@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
                           the_title='Welcome to search4letters on the web!')


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', the_title="Страница не найдена")


@app.route('/viewlog')
@check_logged_in
def view_log() -> 'html':
    if "login" in session:
        with sq.connect('log.db') as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM log WHERE login=?", (session['login'],))
            rows = cur.fetchall()
        titles = ('id', 'ts', 'login', 'Phrase', 'Letters', 'ip', 'browser_string', 'Results')
        return render_template('viewlog.html',
                               the_title='View Log',
                               the_row_titles=titles,
                               the_data=rows,)
    else:
        flash("You have to login firstly")
        return redirect('/login')


def log_request(req: 'flask_request', res: str) -> None:
    with sq.connect('log.db') as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts timestamp default current_timestamp,
            login varchar (32) not null,
            phrase varchar (128) not null,
            letters varchar (32) not null,
            ip varchar(16) not null,
            browser_string varchar(256) not null,
            results varchar(64) not null
        );""")
        print("Opened database successfully")
        cur.execute("INSERT INTO log(login, phrase, letters, ip, browser_string, results) VALUES (?, ?, ?, ?, ?, ?)",
                    (session['login'], req.form['phrase'], req.form["letters"], req.remote_addr, str(req.user_agent), res))
        con.commit()
        print("Records created successfully")
        cur.close()


def do_register(req):
    with sq.connect('users.db') as db:
        cur = db.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name varchar (32) not null,
                    login varchar (32) not null,
                    password varchar (32) not null
                );""")
        cur.execute("""INSERT INTO users(name, login, password) VALUES(?, ?, ?)""", (req.form['name'],
                                                                                         req.form['email'],
                                                                                         req.form["psw"]))

@app.route('/logout')
def log_out():
    session.pop('login', None)  # удаление данных о посещениях
    return redirect('/login')

app.secret_key = 'FijdkdajdsfaskUU2'

if __name__ == '__main__':
    app.run(debug=True)
