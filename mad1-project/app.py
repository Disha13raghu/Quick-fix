from flask import Flask
from backend.database import db
from backend.config import developersconfig
from flask_restful import Api
from backend.api import getservice,getusers,getrequest,getblacklisted,search_user,accept_requests,user_service



app= None

def setup(): 
     
    app= Flask(__name__)
    app.config.from_object(developersconfig)
    app.config['SECRET_KEY'] = 'dsncjncksns'
    db.init_app(app)
    
    app.app_context().push()
    api = Api(app)
    
    #api routes
    api.add_resource(getservice,'/api/admin/getservice')
    api.add_resource(getusers,'/api/admin/getusers')
    api.add_resource(getrequest,'/api/admin/getrequest')
    api.add_resource(getblacklisted,'/api/admin/getblacklisted')
    api.add_resource(search_user,'/api/admin/search_user')
    
    api.add_resource(accept_requests,'/api/professional/accept_requests')
    
    api.add_resource(user_service,'/api/customer/user_service')
    

setup()
from backend.controllers import * 


db.create_all()

if __name__ == '__main__':
	
	app.run(
	debug=True)
