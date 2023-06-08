from flask import Flask, render_template, request, Markup
import sqlite3, subprocess

app = Flask(__name__)

def connect_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
@app.template_filter('safe')
def safe_filter(s):
    return Markup(s)
@app.route('/')
def index():
    return render_template('dashboard.html')

#Dipercantik dan dibuatkan skenarionya
@app.route('/xss1', methods=['GET', 'POST'])
def xss_post():
    if request.method == 'POST':
        name = request.form.get('name')
        return render_template('xss-post.html', name=name)
    return render_template('xss-post.html')

#Dipercantik dan dibuatkan skenarionya
@app.route('/xss2', methods=['GET'])
def xss_get():
    name = request.args.get('name')
    return render_template('xss-get.html', name=name)

#Next munculin SQL Error Syntax nya
@app.route('/login1', methods=['GET', 'POST'])
def login_post():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor()

        # Query yang rentan terhadap serangan SQL Injection
        query = "SELECT * FROM users WHERE username = '{}' AND password = '{}'".format(username, password)

        cursor.execute(query)
        user = cursor.fetchone()

        conn.close()

        if user:
            message = "Login berhasil"
        else:
            message = "Username atau password salah"

    return render_template('sqli-post.html',message=message)

@app.route('/login2', methods=['GET', 'POST'])
def login_get():
    message = None
    # Mengambil data dari parameter query string
    username = request.args.get('username')
    password = request.args.get('password')

    if username and password:
        conn = connect_db()
        cursor = conn.cursor()

        # Query yang rentan terhadap serangan SQL Injection
        query = "SELECT * FROM users WHERE username = '{}' AND password = '{}'".format(username, password)

        cursor.execute(query)
        user = cursor.fetchone()

        conn.close()

        if user:
            message = "Login berhasil"
        else:
            message = "Username atau password salah"

    return render_template('sqli-get.html', message=message)

#Dipercantik dan dibuatkan skenarionya
@app.route('/command1', methods=['GET', 'POST'])
def execute_command_post():
    if request.method == 'POST':
        command = request.form.get('command')
        result = ''

        if command:
            # DANGER: Potensi kerentanan Command Injection
            result = subprocess.getoutput(command)

        return render_template('command-post.html', command=command, result=result)
    
    return render_template('command-post.html')

#Dipercantik dan dibuatkan skenarionya
@app.route('/command2', methods=['GET'])
def execute_command_get():
    command = request.args.get('command')
    result = ''

    if command:
        # DANGER: Potensi kerentanan Command Injection
        result = subprocess.getoutput(command)

    return render_template('command-get.html', command=command, result=result)

if __name__ == '__main__':
    app.run(debug=True)