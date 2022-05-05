from flask import Flask, render_template, request, escape
from vsearch4web import search4letters
import sqlite3 as sq

app = Flask(__name__)


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


@app.route('/viewlog')
def view_log() -> 'html':
    content = []
    with open('vsearch.log') as log:
        for line in log:
            content.append([])
            for item in line.split('|'):
                content[-1].append(escape(item))
    titles = ('Form Data', 'Remote_addr', 'User_agent', 'Results')
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=titles,
                           the_data=content,)


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


if __name__ == '__main__':
    app.run(debug=True)
