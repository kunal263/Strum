from flask import Flask, jsonify, g, url_for
from flask_restful import request, abort
import random
import datetime
from models import *

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://0abd06dd1d1346a885a45f2cd1acb02f@sentry.io/2380874",
    integrations=[FlaskIntegration()]
)


@app.route('/api/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    profilepic = request.json.get('profileurl')
    if username is None or password is None:
        return jsonify({'message':'fill in the fieldsp'})  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)  # existing user
    user = User(username=username)
    user.hash_password(password)
    user.profile_pic=profilepic
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}), 201





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
    description=request.json.get('description')
    project=Project(name = projectname)
    projectid=random.randint(1,1001)
    project.ProjID=projectid
    project.adminID=userid
    project.description=description
    pumap=UserProject(UserID=userid)
    pumap.ProjID=projectid
    db.session.add(pumap)
    db.session.add(project)
    db.session.commit()

    return jsonify({'projectid':projectid,'projectname':projectname,'AdminID':userid,'description':description})

@app.route('/api/addusers',methods = ['POST'])
@auth.login_required
def add_users():
    userid=request.json.get('userid')
    projectid=request.json.get('projectid')
    if User.query.filter_by(id=userid).first() is None:
        abort(400) #non existing user
    newuser=UserProject(UserID=userid)
    newuser.ProjID=projectid
    db.session.add(newuser)
    db.session.commit()

    return jsonify({'Added user':userid , 'Project' :projectid})

@app.route('/api/addtasks',methods=['POST'])
@auth.login_required
def add_tasks():
    taskname=request.json.get('taskname')
    taskid=random.randint(1,1001)
    userid=g.user.id
    task=PersonalTasks(name=taskname)
    task.UserID=userid
    task.id=taskid
    db.session.add(task)
    db.session.commit()

    return jsonify({'task':taskname , 'taskid': taskid})

@app.route('/api/addprojecttasks',methods=['POST'])
@auth.login_required
def add_ptasks():
    userid=request.json.get('userid')
    taskname=request.json.get('taskname')
    projectid=request.json.get('projectid')
    deadline=request.json.get('deadline')
    priority=request.json.get('priority')
    task=Tasks(name=taskname)
    taskid=random.randint(1,1001)
    task.taskID=taskid
    task.status="ongoing"
    task.deadline=datetime.datetime.strptime(deadline,'%d-%m-%y').date()
    task.priority=priority
    task.ProjID=projectid
    task.UserID=userid
    if Project.query.filter_by(ProjID=projectid).first() is None:
        abort(400)
    db.session.add(task)
    db.session.commit()

    return jsonify({'taskid':taskid,'taskname':taskname})


@app.route('/api/getprojects')
@auth.login_required
def get_projects():
    userid=g.user.id
    projects=[]
    info=[]
    projects=UserProject.query.filter_by(UserID=userid).all()
    if projects is None:
        abort(400)  #no projects
    for project in projects:
        temp_id=project.ProjID
        projectid=temp_id
        projectname=Project.query.filter_by(ProjID=temp_id).first().name
        admin=Project.query.filter_by(ProjID=temp_id).first().adminID
        adminname=User.query.filter_by(id=admin).first().username
        info.append({'projectid':projectid,'projectname':projectname,'adminname':adminname})

    return jsonify({'projects':info})

@app.route('/api/<int:projectid>/getdetails')
@auth.login_required
def get_details(projectid):
    users=[]
    taskinfo=[]
    description=Project.query.filter_by(ProjID=projectid).first().description
    userids=UserProject.query.filter_by(ProjID=projectid).all()
    tasks=Tasks.query.filter_by(ProjID=projectid).all()
    for id in userids:
        userid=id.UserID
        uname=User.query.filter_by(id=id.UserID).first().username
        profileurl=User.query.filter_by(id=id.UserID).first().profile_pic
        users.append({'userid':userid,'username':uname,'profileurl':profileurl})
    for task in tasks:
        tname=task.name
        taskid = task.taskID
        task_userid=task.UserID
        priority=task.priority
        deadline=task.deadline
        status=task.status
        taskinfo.append({'taskname':tname,'taskid':taskid,'userid':task_userid,'priority':priority,'deadline':deadline,'status':status})


    return jsonify({'description':description,'users':users,'tasks':taskinfo})


@app.route('/api/<int:taskid>/gettaskdetails')
@auth.login_required
def get_task_details(taskid):
    name=Tasks.query.filter_by(taskID=taskid).first().name
    deadline=Tasks.query.filter_by(taskID=taskid).first().deadline
    priority=Tasks.query.filter_by(taskID=taskid).first().priority
    return jsonify({'taskname':name , 'deadline' : deadline , 'priority' : priority})

@app.route('/api/getusers')
@auth.login_required
def get_user():
    userid=g.user.id
    username=User.query.filter_by(id=userid).first().username
    profileurl=User.query.filter_by(id=userid).first().profile_pic
    return jsonify({'username':username,'userid':userid,'profileurl':profileurl})

@app.route('/api/updatestatus',methods=['PUT'])
@auth.login_required
def update_status():
    taskid=request.json.get('taskid')
    new_status=request.json.get('status')
    taskrow=Tasks.query.filter_by(taskID=taskid).first()
    taskrow.status=new_status
    db.session.commit()
    return {'message':'status updated'}
























if __name__=='__main__':

    app.run(debug=True)


