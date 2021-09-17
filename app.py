from flask import Flask, redirect, url_for, render_template


app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/<name>')
def user(name):
    return f"Hello {name}"

if __name__ == '__main__':
    app.run(debug=True)