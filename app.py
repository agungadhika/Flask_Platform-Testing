import json
import sys
from flask import Flask, jsonify, render_template, request, Markup
import sqlite3
import subprocess
from lxml import etree
from pymongo import MongoClient

app = Flask(__name__)


def connect_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def connect_mongo():
    client = MongoClient("mongodb://root:toor@mongo")
    db = client['dbuser']
    return db


@app.template_filter('safe')
def safe_filter(s):
    return Markup(s)


@app.route('/')
def index():
    return render_template('dashboard.html')

# Dipercantik dan dibuatkan skenarionya


@app.route('/xss1', methods=['GET', 'POST'])
def xss_post():
    if request.method == 'POST':
        name = request.form.get('name')
        return render_template('xss-post.html', name=name)
    return render_template('xss-post.html')

# Dipercantik dan dibuatkan skenarionya


@app.route('/xss2', methods=['GET'])
def xss_get():
    name = request.args.get('name')
    return render_template('xss-get.html', name=name)

# Next munculin SQL Error Syntax nya


@app.route('/login1', methods=['GET', 'POST'])
def login_post():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor()

        # Query yang rentan terhadap serangan SQL Injection
        query = "SELECT * FROM users WHERE username = '{}' AND password = '{}'".format(
            username, password)

        cursor.execute(query)
        user = cursor.fetchone()

        conn.close()

        if user:
            message = "Login berhasil"
        else:
            message = "Username atau password salah"

    return render_template('sqli-post.html', message=message)


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
        query = "SELECT * FROM users WHERE username = '{}' AND password = '{}'".format(
            username, password)

        cursor.execute(query)
        user = cursor.fetchone()

        conn.close()

        if user:
            message = "Login berhasil"
        else:
            message = "Username atau password salah"

    return render_template('sqli-get.html', message=message)

# Dipercantik dan dibuatkan skenarionya


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

# Dipercantik dan dibuatkan skenarionya


@app.route('/command2', methods=['GET'])
def execute_command_get():
    command = request.args.get('command')
    result = ''

    if command:
        # DANGER: Potensi kerentanan Command Injection
        result = subprocess.getoutput(command)

    return render_template('command-get.html', command=command, result=result)


@app.route('/xxe1', methods=['GET', 'POST'])
def xxe_post():
    if request.method == "POST":
        xml = request.form.get('xml')
        if xml:
            parser = etree.XMLParser(resolve_entities=True)
            try:
                tree: etree._Element = etree.fromstring(xml, parser)
                root: etree._Element = tree.getroottree()
                data = root.findtext('data')
                return "<root><data>%s</data></root>" % data
            except Exception as e:
                return "<root><data>%s</data></root>" % e
    return render_template('xxe-post.html')


@app.route('/xxe2', methods=['GET'])
def xxe_get():
    xml = request.args.get('xml')
    if xml:
        parser = etree.XMLParser(resolve_entities=True)
        try:
            tree: etree._Element = etree.fromstring(xml, parser)
            root: etree._Element = tree.getroottree()
            result = root.findtext('data')
            return render_template('xxe-get.html', result=result, xml=xml)
        except Exception as e:
            return render_template('xxe-get.html', result=e, xml=xml)
    return render_template('xxe-get.html', xml=xml)


@app.route("/nosql1", methods=['POST', 'GET'])
def nosql_post():
    """
    exploit:
    ```sh
    curl -X POST "http://localhost/nosql1" --json '{"username":{"$ne":"foo"},"password":{"$ne":"foo"}}' -vvv
    ```
    """
    if request.method == "POST":
        con = connect_mongo()
        # Danger: Potential NoSQL Injection vulnerability
        users = con['user'].find(request.json)
        serialized_users = [
            {**user, '_id': str(user['_id'])} for user in users
        ]
        return jsonify(serialized_users)
    return render_template('nosql-post.html')


@app.route("/nosql2", methods=['GET'])
def nosql_get():
    """
    exploit:
    ```url
    http://localhost/nosql2?query={}
    http://localhost/nosql2?query={"username":{"$ne":"foo"}}
    ```
    """
    query = request.args.get('query')
    serialized_users = []
    if query:
        con = connect_mongo()
        users = con['user'].find(json.loads(query))
        serialized_users = [
            {**user, '_id': str(user['_id'])} for user in users
        ]
    return render_template('nosql-get.html', users=serialized_users)


if __name__ == '__main__':
    app.run(debug=True)
