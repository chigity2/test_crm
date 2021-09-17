from flask import Flask, redirect, url_for, render_template


app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/client/<name>')
def client(name):
    return render_template("client.html", name = name)

if __name__ == '__main__':
    app.run(debug=True)