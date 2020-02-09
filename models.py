from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey , Date
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature , SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from flask_httpauth import HTTPBasicAuth
from datetime import date


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///taskdatabase.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='secret'
db=SQLAlchemy(app)
auth=HTTPBasicAuth()



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True)
    password_hash = db.Column(db.String(128))
    email=db.Column(db.String(30))
    profile_pic=db.Column(db.String(200))
    projects=db.relationship('Project', secondary='user_project' ,backref='users')


    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user





class Project(db.Model):
    __tablename__ = 'projects'
    ProjID=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),index=True)
    adminID=db.Column(db.Integer,ForeignKey(User.id))
    description=db.Column(db.String(30))



class UserProject(db.Model):
    __tablename__='user_project'
    UserID=db.Column(db.Integer,ForeignKey(User.id))
    ProjID=db.Column(db.Integer,ForeignKey(Project.ProjID),index=True)
    id=db.Column(db.Integer,primary_key=True)




class Tasks(db.Model):
    __tablename__ = 'tasks'
    taskID=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),unique=True)
    deadline=db.Column(db.Date,default=date.today())
    priority=db.Column(db.String(30))
    ProjID=db.Column(db.Integer,ForeignKey(Project.ProjID))
    UserID=db.Column(db.Integer,ForeignKey(User.id))
    status=db.Column(db.String(20))


class PersonalTasks(db.Model):
    UserID=db.Column(db.Integer,ForeignKey(User.id))
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20))

