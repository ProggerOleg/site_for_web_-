from flask import Flask, render_template, request, session
from vsearch4web import search4letters
import sqlite3 as sq
from checker import check_logged_in


app = Flask(__name__)


@app.route("/login")
def login():
    return render_template("login.html", title="Авторизация")

@app.route("/register")
def register():
    return render_template("register.html", title="Регистрация")

#@app.route('/login')
#def do_login() -> str:
#    session['logged_in'] = True
#    return "You are now logged in"


#@app.route('/logout')
#def do_logout() -> str:
#    session.pop('logged_in')
#    return "You are now logged out"


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
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
                           the_title='Welcome to search4letters on the web!')

@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', the_title="Страница не найдена")


@app.route('/viewlog')
@check_logged_in
def view_log() -> 'html':
    content = []
    with sq.connect('log.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM log")
        rows = cur.fetchall()
    titles = ('id', 'ts', 'Phrase', 'Letters', 'ip', 'browser_string', 'Results')
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=titles,
                           the_data=rows,)


def log_request(req: 'flask_request', res: str) -> None:
    with sq.connect('log.db') as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts timestamp default current_timestamp,
            phrase varchar (128) not null,
            letters varchar (32) not null,
            ip varchar(16) not null,
            browser_string varchar(256) not null,
            results varchar(64) not null
        );""")
        print("Opened database successfully")
        cur.execute("INSERT INTO log(phrase, letters, ip, browser_string, results) VALUES (?, ?, ?, ?, ?)",
                    (req.form['phrase'], req.form["letters"], req.remote_addr, str(req.user_agent), res))
        con.commit()
        print("Records created successfully")
        cur.close()

app.secret_key = 'Ding_dong'

if __name__ == '__main__':
    app.run(debug=True)
