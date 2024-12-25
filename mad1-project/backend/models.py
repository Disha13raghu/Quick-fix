from .database import db
from datetime import date, timedelta

# Many-to-many relationship tables
#Userservices = db.Table('service_by_user',
 #   db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True),
  #  db.Column('service_id', db.Integer, db.ForeignKey('service.service_id'), primary_key=True)
#)

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String, nullable=False, unique=True)
    role = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    pin_code = db.Column(db.Integer)
    service_id = db.Column(db.Integer, db.ForeignKey("service.service_id", ondelete='CASCADE'))
    user_status = db.Column(db.String, nullable=False)
    professional_status= db.Column(db.String)
    professional_rating=db.Column(db.Integer,default=0)
    name_user= db.Column(db.String)
    
#relationships
   # one to many relationship with service_requests 
    requested_from_professional= db.relationship('ServiceRequest', backref='user', lazy=True,foreign_keys='ServiceRequest.professional_id')  
    
    
    # Many-to-many relationship with Service through `Userservices`
    #services = db.relationship('Service', secondary=Userservices, lazy='subquery', backref=db.backref('users', lazy=True))

class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_id = db.Column(db.Integer, db.ForeignKey("service.service_id", ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete='CASCADE'), nullable=False)
    user_name =db.Column(db.String, db.ForeignKey("user.user_name"))
    name_user=db.Column(db.String, db.ForeignKey("user.name_user"))
    address=db.Column(db.String,nullable=False)
    pin_code=db.Column(db.Integer,nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete='CASCADE'))
    service_status = db.Column(db.String, nullable=False)
    date_of_request = db.Column(db.Date, nullable=False, default=date.today)
    date_of_completion = db.Column(db.Date, nullable=True)
    remarks=db.Column(db.String)
    ratings=db.Column(db.Integer, default=0)
    service_name=db.Column(db.String,nullable=False)

class Service(db.Model):
    __tablename__ = 'service'
    service_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_name = db.Column(db.String, nullable=False)
    service_description = db.Column(db.String, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    service_rating=db.Column(db.Integer,default=0)
    
    #one to many relationship with service_request
    requests_for_services= db.relationship('ServiceRequest', backref='service', lazy=True)

class RejectedRequest(db.Model):
    __tablename__ = 'rejected_request'
    rejected_id= db.Column('rejected_id',db.Integer, primary_key=True, autoincrement=True)
    professional_id = db.Column('professional_id', db.Integer, db.ForeignKey('user.user_id'))
    request_id=db.Column('request_id', db.Integer, db.ForeignKey('service_request.request_id'))
