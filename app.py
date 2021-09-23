from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
from sqlalchemy.engine import url
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import desc
import secretstuff

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkeythings'
## app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(secretstuff.dbuser, secretstuff.dbpass, secretstuff.dbhost, secretstuff.dbname)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

## CREATE THE DATABASE TABLES BELOW
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
    subPreQualAmount = db.Column(db.Integer, default=0)
    subAddress2 = db.Column(db.String(45))
    subCity = db.Column(db.String(45))
    subState = db.Column(db.String(45))
    subZip = db.Column(db.String(45))
    subDoesPrevailing = db.Column(db.Integer, default=0)
    notes = db.relationship('subnotes', backref='sub_Id', lazy=True)

    def __repr__(self) -> str:
        return super().__repr__()

class tradelist(db.Model):
    tradeId = db.Column(db.Integer, primary_key=True)
    tradeCode = db.Column(db.String(45))
    tradeName = db.Column(db.String(45))

    def __repr__(self) -> str:
        return super().__repr__()

class tradesublink(db.Model):
    tradesublinkID = db.Column(db.Integer, primary_key=True)
    tradeId = db.Column(db.Integer, ForeignKey("tradelist.tradeId"))
    subId = db.Column(db.Integer, ForeignKey("subcontractors.subId"))

    def __repr__(self) -> str:
        return super().__repr__()

class subnotes(db.Model):
    subNoteId = db.Column(db.Integer, primary_key=True)
    subId = db.Column(db.Integer, ForeignKey("subcontractors.subId"))
    subNote = db.Column(db.String(200))
    noteType = db.Column(db.String(45))
    userId = db.Column(db.Integer, ForeignKey("users.userId"))
    noteDateCreated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return super().__repr__()

class users(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    userFirst = db.Column(db.String(45))
    userLast = db.Column(db.String(45))
    userEmail = db.Column(db.String(45))
    userUsername = db.Column(db.String(45))

    def __repr__(self) -> str:
        return super().__repr__()

class subcontacts(db.Model):
    subcontactId = db.Column(db.Integer, primary_key=True)
    contactName = db.Column(db.String(100))
    contactEmail = db.Column(db.String(100))
    contactCell = db.Column(db.String(100))
    contactLastName = db.Column(db.String(100))
    subId = db.Column(db.Integer, ForeignKey("subcontractors.subId"))

    def __repr__(self) -> str:
        return super().__repr__()

##SETUP THE MAIN PAGE ROUTES BELOW
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/sublist')
def sublist():
    clientInfo = subcontractors.query.all()
    return render_template("sublist.html", clientinfo=clientInfo)

@app.route('/testing')
def testing():
    tasks = taskstable.query.all()
    tradesublinklist = tradesublink.query.all()
    contactinfo = subcontacts.query.all()
    clientInfo = subcontractors.query.filter_by(subId=1).first()
    subtradelist = db.session.query(tradelist, tradesublink).filter(tradesublink.subId==1).all()
    subNotes = subnotes.query.join(users).add_columns(users.userUsername, subnotes.noteDateCreated, subnotes.subNote, subnotes.noteType).filter(subnotes.subId==1).order_by(desc(subnotes.noteDateCreated)).all()
    return render_template('testing.html', tasks=tasks, clientInfo=clientInfo, subtradelist=subtradelist, sub1Notes=subNotes, tslinklist=tradesublinklist, contactinfo=contactinfo)

@app.route('/client/<int:id>')
def client(id):
    tasks = taskstable.query.all()
    clientInfo = subcontractors.query.filter_by(subId=id).first()
    alltrades = tradelist.query.all()
    contactinfo = subcontacts.query.filter_by(subId=id).all()
    subtradelist = tradesublink.query.join(tradelist).add_columns(tradelist.tradeCode, tradelist.tradeName, tradelist.tradeId, tradesublink.tradesublinkID).filter(tradesublink.subId==id).all()
    subNotes = subnotes.query.join(users).add_columns(users.userUsername, subnotes.noteDateCreated, subnotes.subNote, subnotes.noteType).filter(subnotes.subId==id).order_by(desc(subnotes.noteDateCreated)).all()
    return render_template('client.html', tasks=tasks, clientInfo=clientInfo, subtradelist=subtradelist, subNotes=subNotes, id=id, alltrades=alltrades, contactinfo=contactinfo)

## add form actions below
@app.route('/addTrade', methods=["POST","GET"])
def addTrade():
    if request.method == "POST":
        newTradeCode = request.form['tradeCode']
        newTradeName = request.form['tradeName']
        new_trade = tradelist(tradeCode=newTradeCode, tradeName=newTradeName)
        try:
            db.session.add(new_trade)
            db.session.commit()
            return redirect('/testing')

        except:
            return 'there was an unknown error adding trade'

@app.route('/addNote', methods=["POST","GET"])
def addNote():
    if request.method == "POST":
        newsubNote = request.form['addNewTaskTextArea']
        newusername = 1
        newNoteType = request.form['newNoteType']
        newNoteSubId = request.form['newNoteSubId']
        new_note = subnotes(subId=newNoteSubId, subNote=newsubNote, noteType=newNoteType, userId=newusername)
        try:
            db.session.add(new_note)
            db.session.commit()
            return redirect(url_for('client', id=newNoteSubId))

        except:
            return 'there was an unknown error adding note'

@app.route('/addPhoneNote', methods=["POST","GET"])
def addPhoneNote():
    if request.method == "POST":
        newsubNote = request.form['logCallTextArea']
        newusername = 1
        newNoteType = request.form['newNoteType']
        newNoteSubId = request.form['newNoteSubId']
        new_note = subnotes(subId=newNoteSubId, subNote=newsubNote, noteType=newNoteType, userId=newusername)
        try:
            db.session.add(new_note)
            db.session.commit()
            return redirect(url_for('client', id=newNoteSubId))

        except:
            return 'there was an unknown error adding note'

@app.route('/addSub', methods=["POST","GET"])
def addPSub():
    if request.method == "POST":
        subName = request.form['subName']
        subAddress = request.form['subAddress']
        subAddress2 = request.form['subAddress2']
        subCity = request.form['subCity']
        subState = request.form['subState']
        subPhone = request.form['subPhone']
        subZip = request.form['subZip']
        subFax = request.form['subFax']
        new_note = subcontractors(subName=subName, subAddress=subAddress, subAddress2=subAddress2, subCity=subCity, subState=subState, subZip=subZip, subPhone=subPhone, subFax=subFax)
        try:
            db.session.add(new_note)
            db.session.commit()
            return redirect(url_for('sublist'))

        except:
            return 'there was an unknown error adding sub'

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
def clearTask(id):
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

@app.route('/clearTrade/<int:id>/<int:page>')
def clearTrade(id, page):
    tradetoClear = tradesublink.query.filter_by(tradesublinkID=id).first()

    try:
        db.session.delete(tradetoClear)
        db.session.commit()
        return redirect(url_for('client', id=page))
    except:
        return "there was en error clearing task"

@app.route('/addTradeLink', methods=["POST","GET"])
def tradeToAdd():
    
    if request.method == "POST":
        trade_id = request.form['addTradeSelect']
        sub_id = request.form['newTradeSubId']
        tradeToAdd = tradesublink(subId=sub_id, tradeId=trade_id)

        try:
            db.session.add(tradeToAdd)
            db.session.commit()
            return redirect(url_for('client', id=sub_id))
        except:
            return "there was en error adding trade"

@app.route('/addContact', methods=["POST","GET"])
def contactToAdd():
    
    if request.method == "POST":
        contact_name = request.form['firstname']
        lastname = request.form['lastname']
        contactEmail = request.form['email']
        contactCell = request.form['cell']
        sub_id = request.form['newTradeSubId']
        contactToAdd = subcontacts(subId=sub_id, contactName=contact_name, contactLastName=lastname, contactEmail=contactEmail, contactCell=contactCell)

        try:
            db.session.add(contactToAdd)
            db.session.commit()
            return redirect(url_for('client', id=sub_id))
        except:
            return "there was en error adding contact"
## ERROR HANDLER OBJECTS BELOW
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)