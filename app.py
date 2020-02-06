from flask import Flask, jsonify, g
from flask_restful import request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import engine
import random


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///taskdatabase.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='secret'
db=SQLAlchemy(app)
auth=HTTPBasicAuth()

from models import db


@app.route('/api/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if User.query.filter_by(username = username).first() is not None:
        abort(400)    # existing user
    user = User(username = username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username }), 201





@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/api/addproject',methods = ['POST'])
@auth.login_required
def add_project():
    userid=g.user.id
    projectname=request.json.get('projectname')
    project=Project(name = projectname)
    projectid=random.randint(1,1001)
    project.ProjID=projectid
    project.adminID=userid
    pumap=UserProject(UserID=userid)
    pumap.ProjID=projectid
    db.session.add(pumap)
    db.session.add(project)
    db.session.commit()

    return jsonify({'projectname':projectname,'AdminID':userid})

@app.route('/api/addusers',methods = ['POST'])
@auth.login_required
def add_users():
    username=request.json.get('username')
    projectname=request.json.get('projectname')
    if User.query.filter_by(username = username).first() is None:
        abort(400) #non existing user
    add=User.query.filter_by(username = username).first()
    userid=add.id
    project=Project.query.filter_by(name=projectname).first()
    projid=project.ProjID
    newuser=UserProject(UserID=userid)
    newuser.ProjID=projid
    db.session.add(newuser)
    db.session.commit()

    return jsonify({'Added user':username , 'Project' :projectname})

@app.route('/api/addtasks',methods=['POST'])
@auth.login_required
def add_tasks():
    taskname=request.json.get('taskname')
    userid=g.user.id
    task=Tasks(name=taskname)
    taskid=random.randint(1,1001)
    task.taskID=taskid
    tumap=UserTask(UserID=userid)
    tumap.taskID=taskid
    db.session.add(task)
    db.session.add(tumap)
    db.session.commit()

    return jsonify({'task':taskname})

@app.route('/api/addprojecttasks',methods=['POST'])
@auth.login_required
def add_ptasks():
    username=request.json.get('username')
    userid=User.query.filter_by(username=username).first().id
    taskname=request.json.get('taskname')
    projectname=request.json.get('projectname')
    task=Tasks(name=taskname)
    taskid=random.randint(1,1001)
    task.taskID=taskid
    if Project.query.filter_by(name=projectname).first() is None:
        abort(400)
    projectid=Project.query.filter_by(name=projectname).first().ProjID
    ptmap=ProjectTask(ProjID=projectid)
    ptmap.taskID=taskid
    tumap=UserTask(UserID=userid)
    tumap.taskID=taskid
    db.session.add(task)
    db.session.add(ptmap)
    db.session.add(tumap)
    db.session.commit()

    return jsonify({'task':taskname,'project':projectname})


@app.route('/api/getprojects')
@auth.login_required
def get_projects():
    userid=g.user.id
    projectnames=[]
    admins=[]
    users=[]
    projects=UserProject.query.filter_by(UserID=userid).all()
    if projects is None:
        abort(400)  #no projecs
    for project in projects:
        temp_id=project.ProjID
        projectnames.append(Project.query.filter_by(ProjID=temp_id).first().name)
        admins.append(Project.query.filter_by(ProjID=temp_id).first().adminID)
    for admin in admins:
        users.append(User.query.filter_by(id=admin).first().username)

    return jsonify({'projects':projectnames,'admins':users})


#@app.route('/api/getprojectdetails')
#@auth.login_required
#def get_details():






if __name__=='__main__':

    app.run(debug=True)


