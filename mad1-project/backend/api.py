from flask_restful import Resource
from flask import jsonify, make_response, request
from backend.models import User, Service,ServiceRequest,RejectedRequest
import os
from datetime import datetime
from werkzeug.security import generate_password_hash as gph
from werkzeug.security import check_password_hash as cph
from backend.database import db




def isadmin(user_name,password):
    u = User.query.filter_by(user_name=user_name, role=1).first()
    if u and cph(u.password,password):       
        return True
    return False

def isprofessional(user_name,password):
    u = User.query.filter_by(user_name=user_name, role=2).first()
    if u and cph(u.password,password):       
        return True
    return False

def iscustomer(user_name,password):
    u = User.query.filter_by(user_name=user_name, role=3).first()
    if u and cph(u.password,password):       
        return True
    return False    
    
#1)admin functionalities

# service related
class getservice(Resource):
    
    #
    def get(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        
        if isadmin(user_name,password):
            service=Service.query.all()
            services={}
            
            services["services"]=  [{'id':s.service_id,'name':s.service_name,'description':s.service_description,"ratings":s.service_rating}for s in service ]
            
            if services:
               return make_response(jsonify(services),200)
            else:
               d={"message":"No service found"}
               return make_response(jsonify(d),401)
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401)    
        
    def post(self):
        
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        service_name=request.json.get("service_name")
        service_description=request.json.get("service_description")
        price=request.json.get("price")
        time_required=request.json.get("time_required")
        
        if isadmin(user_name,password):
            
            service=Service(service_name=service_name,service_description=service_description,price=price,time_required=time_required,service_rating=0)
            db.session.add(service)
            db.session.commit()
            d={"message":"Service added successfully!!"}
            return make_response(jsonify(d),200)
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401) 
        
        
        
    def delete(self):  
        
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        
        if isadmin(user_name,password):
            ServiceRequest.query.delete()
            service=Service.query.all()
            if service:
                for s in service:
                    path = f"./static/service_images/{s.service_id}.jpg"
                    os.remove(path)    
                    user= User.query.filter_by(service_id=s.service_id).all()
                    for u in user:
                        u.professional_status="Service_not_available"                                        
                    db.session.delete(s)
                db.session.commit()
                d={"message":"All services and professionals related to them deleted successfully!!"}
                return make_response(jsonify(d),200)
            else:
                d={"message":"No Service Found"}    
                return make_response(jsonify(d),401)
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401) 
        
    def put(self):  
        
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        service_id=request.json.get("service_id")
        service_name=request.json.get("service_name")
        service_description=request.json.get("service_description")
        price=request.json.get("price")
        time_required=request.json.get("time_required")
        
        
        if isadmin(user_name,password):
            
            service=Service.query.filter_by(service_id=service_id).first()
            if service:
                
                service.service_name= service_name
                service.service_description=service_description
                service.price=price
                service.time_required=time_required
                db.session.commit()
                d={"message":"Service updated successfully!!"}
                return make_response(jsonify(d),200)
            else:
                d={"message":"Service not found"}    
                return make_response(jsonify(d),401)
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401)
        



class getusers(Resource):
    #get details of all users 
    def get(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        
        if isadmin(user_name,password):
            customers=User.query.filter_by(role=3).all()
            professionals=User.query.filter_by(role=2).all()
            users={}
            
            users["customers"]=  [{'id':c.user_id,'name':c.name_user,'user_name':c.user_name,'address':c.address,'pincode':c.pin_code}for c in customers ]
            users["professionals"]=  [{'id':p.user_id,'name':p.name_user,'user_name':p.user_name,'address':p.address,'pincode':p.pin_code,'service_id':p.service_id,'rating':p.professional_rating}for p in professionals ]
            
            if users:
              return make_response(jsonify(users),200)
            else:
              d={"message":"No users found"}
              return make_response(jsonify(d),401)  
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401)
    
    
    #delete all users except admin   
    def delete(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        
        if isadmin(user_name,password):
            
            user=User.query.filter(User.role!=1).all()
            if user:
                for u in user:
                    path = f"./static/files/{u.user_id}.pdf"
                    os.remove(path)                    
                    db.session.delete(u)
                db.session.commit()
                d={"message":"All Users deleted successfully!!"}
                return make_response(jsonify(d),200)
            else:
                d={"message":"No User Found"}    
                return make_response(jsonify(d),401)
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401)
        
        
           
             

class getrequest(Resource):
    #get all the requests
    def get(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        
        if isadmin(user_name,password):
            closed=ServiceRequest.query.filter_by(service_status="Closed").all()
            pending=ServiceRequest.query.filter_by(service_status="Pending").all()
            active=ServiceRequest.query.filter_by(service_status="Active").all()
            requests={}
            
            requests["Active"]=  [{'id':a.request_id,'service_name':a.service_name,'customer_name':a.user_name,'professional_assigned':a.professional_id,'address':a.address,'pincode':a.pin_code}for a in active ]
            requests["Pending"]=  [{'id':p.request_id,'service_name':p.service_name,'customer_name':p.user_name,'address':p.address,'pincode':p.pin_code}for p in pending ]
            requests["Closed"]=  [{'id':c.request_id,'service_name':c.service_name,'customer_name':c.user_name,'professional_assigned':c.professional_id,'address':c.address,'pincode':c.pin_code}for c in closed ]
            return make_response(jsonify(requests),200)
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401)




class getblacklisted(Resource):
    #get all blacklisted users
    def get(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        
        if isadmin(user_name,password):
            customers=User.query.filter_by(role=3,professional_status="Blacklisted").all()
            professionals=User.query.filter_by(role=2,professional_status="Blacklisted").all()
            users={}
            
            users["customers"]=  [{'id':c.user_id,'name':c.name_user,'user_name':c.user_name,'address':c.address,'pincode':c.pin_code}for c in customers ]
            users["professionals"]=  [{'id':p.user_id,'name':p.name_user,'user_name':p.user_name,'address':p.address,'pincode':p.pin_code,'service_id':p.service_id}for p in professionals ]
            
            if users:
              return make_response(jsonify(users),200)
            else:
              d={"message":"No users found"}
              return make_response(jsonify(d),401)  
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401)
       
   
    #blacklist users
    def post(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        
        if isadmin(user_name,password):
            customers=User.query.filter_by(role=3).all()
            professionals=User.query.filter_by(role=2).all()
            for c in customers:
                c.professional_status="Blacklisted"
                
            for c in professionals:
                c.professional_status="Blacklisted"   
            db.session.commit()     
            
            d={"message":"Blacklisted all users"}
            return make_response(jsonify(d),200) 
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401)
    
    
    #delete all blacklisted users
    def delete(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        
        if isadmin(user_name,password):
            users=User.query.filter_by(professional_status="Blacklisted").all()
                
            if users:
                for u in users:
                     db.session.delete(u)
                db.session.commit()
                d={"message":"All Blacklisted Users deleted"}     
                return make_response(jsonify(d),200) 
            else:
              d={"message":"No Blacklisted users found"}
              return make_response(jsonify(d),401)  
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401)
    
    
    #update blacklisted users status i.e. unblacklist them all
    def put(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        
        if isadmin(user_name,password):
            users=User.query.filter_by(professional_status="Blacklisted").all()
                
            if users:
                for u in users:
                     if u.role==2:
                         u.professional_status="Pending"
                     else:
                         u.professional_status=None    
                db.session.commit()
                d={"message":"All Blacklisted Users Unblocked"}     
                return make_response(jsonify(d),200) 
            else:
              d={"message":"No Blacklisted users found"}
              return make_response(jsonify(d),401)  
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401)
    

# to do user related  task by user id


class search_user(Resource):
    def get(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        user_id= request.json.get("user_id")
        
        if isadmin(user_name,password):
            user = User.query.filter_by(user_id=user_id).first()
            
            if user:
                users=  {'id':user.user_id,'name':user.name_user,'user_name':user.user_name,'address':user.address,'pincode':user.pin_code}
                return make_response(jsonify(users),200)
            else:
              d={"message":"User not found"}
              return make_response(jsonify(d),401)  
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401)
  
            
    def delete(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        user_id= request.json.get("user_id")
        
        if isadmin(user_name,password):
            user = User.query.filter_by(user_id=user_id).first()
              
            if user:
               db.session.delete(user)
               db.session.commit()
                                
               return make_response(jsonify(d),200)
            else:
              d={"message":"User not found"}
              return make_response(jsonify(d),401)  
            
        else:
            d={"message":"Wrong access!! Only Admin can access it"}
            return make_response(jsonify(d),401)
        
        

#2)professionals usability  
    
class accept_requests(Resource):
    
    #get all requests
    def get(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        user= User.query.filter_by(user_name=user_name).first()
        
        if isprofessional(user_name,password):
            requests= ServiceRequest.query.filter_by(service_id=user.service_id,service_status="Pending").all()
            
              
            if requests:
               prof_request={}
               prof_request["Requests"] =[{"id":r.service_id, "service_name":r.service_name,"address":r.address,"pin_code":r.pin_code,"customer_name":r.user_name}for r in requests]
                                                
               return make_response(jsonify(prof_request),200)
            else:
              d={"message":"No requests found"}
              return make_response(jsonify(d),401)  
            
        else:
            d={"message":"Wrong access!! Only Professional can access it"}
            return make_response(jsonify(d),401)
        
    #accept all requests
    def post(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        user= User.query.filter_by(user_name=user_name).first()
        
        if isprofessional(user_name,password):
            requests= ServiceRequest.query.filter_by(service_id=user.service_id,service_status="Pending").all()
            rejected= RejectedRequest.query(RejectedRequest.request_id).filter_by(professional_id=user.user_id).all()
              
            if requests:
                for r in requests:
                    if r.request_id not in rejected:
                        r.service_status="Accepted"
                        r.professional_id=user.user_id
                db.session.commit()      
                d={"message":"All requests accepted"}                                
                return make_response(jsonify(d),200)
            else:
              d={"message":"No request found"}
              return make_response(jsonify(d),401)  
            
        else:
            d={"message":"Wrong access!! Only Professional can access it"}
            return make_response(jsonify(d),401)
        
        
     # delete/reject all request   
    def delete(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        user= User.query.filter_by(user_name=user_name).first()
        
        if isprofessional(user_name,password):
            requests= ServiceRequest.query.filter_by(service_id=user.service_id,service_status="Pending").all()
              
            if requests:
                for r in requests:
                    rejected= RejectedRequest(request_id=r.request_id,professional_id=user.user_id)
                    db.session.add(rejected)
                db.session.commit()      
                d={"message":"All requests rejected"}                                
                return make_response(jsonify(d),200)
            else:
              d={"message":"No request found"}
              return make_response(jsonify(d),401)  
            
        else:
            d={"message":"Wrong access!! Only Professional can access it"}
            return make_response(jsonify(d),401)
        
            
#3)user functionality

class user_service(Resource):
    # get all services
    def get(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        user= User.query.filter_by(user_name=user_name).first()
        
        if iscustomer(user_name,password):
            service= Service.query.order_by(Service.service_rating.desc()).all()            
                          
            if service:
                services={}
                services["services"]=[{"id":s.service_id,"service_name":s.service_name,"price":s.price,"time_required":s.time_required,"ratings":s.service_rating}for s in service]
                                           
                return make_response(jsonify(services),200)
            else:
              d={"message":"No service found"}
              return make_response(jsonify(d),401)  
            
        else:
            d={"message":"Wrong access!! Only Customers can access it"}
            return make_response(jsonify(d),401)
    
    #book service    
    def post(self):
        user_name= request.json.get("user_name")
        password= request.json.get("password")
        service_id=request.json.get("service_id")
        address=request.json.get("address")
        pin_code=request.json.get("pin_code")
        
        user= User.query.filter_by(user_name=user_name).first()
        date_of_request=datetime.now()
        
        if iscustomer(user_name,password):
            service= Service.query.filter_by(service_id=service_id).first() 
                                        
            if service:
                requests=ServiceRequest(service_id=service_id,service_name=service.service_name,address=address,pin_code=pin_code,user_id=user.user_id,user_name=user.user_name,service_status="Pending",ratings=0,name_user=user.name_user,date_of_request=date_of_request)           
                db.session.add(requests)
                db.session.commit()
                d={"message":"Service has been booked"}
                                           
                return make_response(jsonify(d),200)
            else:
              d={"message":"No service found"}
              return make_response(jsonify(d),401)  
            
        else:
            d={"message":"Wrong access!! Only Customers can access it"}
            return make_response(jsonify(d),401)
    
            
            
                           
        
            
      
        
                   
        
            
        
          
             
    














