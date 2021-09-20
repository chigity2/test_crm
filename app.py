from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFITACTIONS'] = False

#initialize the db
db = SQLAlchemy(app)

#create db model
class taskList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    done = db.Column(db.Boolean, default=False)

    def __rper__(self):
        return '<task %r>' % self.id


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/client')
def client():
    return render_template("client.html")

@app.route('/tasks', methods=["POST","GET"])
def tasks():

    if request.method == "POST":
        task_name = request.form['task']
        new_task = taskList(task=task_name)

        #push to db
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/tasks')
        except:
            return "there was an error adding that task"

    else:
        tasks = taskList.query.filter_by(done=False)
        return render_template("tasks.html", tasks = tasks)

@app.route('/clear/<int:id>')
def clearTask(id=id):
    taskClear = taskList.query.filter_by(id=id).first()
    taskClear.done = not taskClear.done
    try:
        db.session.commit()
        return redirect('/tasks')
    except:
        return "there was en error clearing task"

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)