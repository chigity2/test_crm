from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
import secretstuff



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkeythings'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(secretstuff.dbuser, secretstuff.dbpass, secretstuff.dbhost, secretstuff.dbname)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class taskstable(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(200))
    userId = db.Column(db.Integer, default=1)
    done = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "id {0} | {1} by {2}".format(self.task_id, self.task_name, self.userId)

class subcontractors(db.Model):
    subId = db.Column(db.Integer, primary_key=True)
    subName = db.Column(db.String(45))
    subAddress = db.Column(db.String(45))
    subPhone = db.Column(db.String(45))
    subFax = db.Column(db.String(45))
    subLabor = db.Column(db.String(45), default="Non-Union")
    subPreQual = db.Column(db.Integer, default=0)
    subPreQualAmount = db.Column(db.Integer)
    subAddress2 = db.Column(db.String(45))
    subCity = db.Column(db.String(45))
    subState = db.Column(db.String(45))
    subZip = db.Column(db.String(45))
    subDoesPrevailing = db.Column(db.Integer, default=0)

    def __repr__(self) -> str:
        return super().__repr__()



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
        new_task = taskstable(task_name=task_name)

        #push to db
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/tasks')
        except:
            return "there was an error adding that task"

    else:
        tasklist = taskstable.query.filter_by(done=0).all()
        return render_template("tasks.html", tasks = tasklist)

@app.route('/clear/<int:id>')
def clearTask(id=id):
    #get ID of the task that was cleared on the task page
    taskClear = taskstable.query.filter_by(task_id=id).first()
    #toggle the "done" column which is a bool
    taskClear.done = not taskClear.done
    #push to database
    try:
        db.session.commit()
        return redirect('/tasks')
    except:
        return "there was en error clearing task"

@app.route('/testing')
def testing():
    tasks = taskstable.query.all()
    clientInfo = subcontractors.query.all()
    return render_template('testing.html', tasks=tasks, clientInfo=clientInfo)

@app.route('/subtest/<int:id>')
def subtest(id=id):
    tasks = taskstable.query.all()
    clientInfo = subcontractors.query.filter_by(subId=id).first()
    return render_template('clienttest.html', tasks=tasks, clientInfo=clientInfo)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)