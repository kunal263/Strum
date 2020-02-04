from datetime import datetime

from flask import Flask
from flask_restful import Resource, Api , request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature , SignatureExpired)
from flask_httpauth import HTTPBasicAuth

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///taskdatabase.sqlite3'
db=SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    userID=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100))
    email=db.Column(db.String(50))
    password=db.Column(db.String(20))
    admins=db.relationship('Project',backref='admin')
    taskrelation=db.relationship('Tasks',backref='user')

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
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
    adminID=db.Column(db.Integer,ForeignKey('users.userID'))
    name=db.Column(db.String(50))
    tasksrelation=db.relationship('Tasks',backref='project')

class Tasks(db.Model):
    __tablename__ = 'tasks'
    taskID=db.Column(db.Integer,primary_key=True)
    projID=db.Column(db.Integer,ForeignKey('projects.ProjID'))
    userID=db.Column(db.Integer,ForeignKey('users.userID'))
    description=db.Column(db.String(50))
    name=db.Column(db.String(30))
    deadline=db.Column(db.DateTime)
    priority=db.Column(db)

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })






if __name__=='__main__':
    db.create_all()
    app.run(debug=True)


