from flask import Flask, request, render_template, redirect, url_for,flash,session
from backend.models import User, Service, ServiceRequest, RejectedRequest
import os
from flask import current_app as app
from backend.database import db
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash as gph
from werkzeug.security import check_password_hash as cph





today=datetime.now()
#current_user
def get_current_user():
    user_id=session.get('id',None)
    current_user= User.query.filter_by(user_id=user_id).first() 

    return current_user

#role based access

def active(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        curr_user = get_current_user()  
        if not curr_user:
            flash("You are not logged in, Try logging in first","danger")
            return redirect("/login")
            
        return fn(*args, **kwargs)
    return decorated_function



def check_access(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            curr_user = get_current_user()  
            if not curr_user:
                flash("You are not logged in!!", "danger")
                return redirect("/login")
            
            if curr_user.role != role:
                flash(f"You are not {role}, try logging in", "danger")
                return redirect("/home")
            
            return fn(*args, **kwargs)  
        return wrapper
    
    return decorator

        
def professional_access(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        curr_user = get_current_user()  
        if curr_user.professional_status == "Blacklisted":
            flash("You have been Blacklisted and can no longer access the website", "danger")
            return redirect("/login")
        if curr_user.professional_status == "Service_not_available":
            flash("Sorry to inform you that the service you have been providing has been deleted due to some reason", "danger")
            return redirect("/login")
        if curr_user.professional_status == "Pending":
            flash("Your profile has still not been accepted. Please wait for a while", "danger")
            return redirect("/login")
        return fn(*args, **kwargs)
    return decorated_function

def wrong_access():
    
        curr_user = get_current_user()  
        if curr_user.professional_status == "Blacklisted":
            flash("You have been Blacklisted and can no longer access the website", "danger")
            return redirect("/login")
        if curr_user.professional_status == "Service_not_available":
            flash("Sorry to inform you that the service you have been providing has been deleted due to some reason", "danger")
            return redirect("/login")
        if curr_user.professional_status == "Pending":
            flash("Your profile has still not been accepted. Please wait for a while", "danger")
            return redirect("/login")        
    
    
        
        
    
        
            
    
    
# current_service
def get_curr_service(service_id):
    service= Service.query.filter_by(service_id=service_id).first()
    return service

#all types of professionals
def get_accepted_professional():
    professional= User.query.filter_by(professional_status= "Accepted").all()
    return professional
    
def get_all_professional():
    professional= User.query.filter_by(role=2).all()
    return professional

def get_pending_professional():
    professional= User.query.filter_by(professional_status= "Pending").order_by(User.user_id.desc()).all()
    return professional

def get_blacklisted_professional():
    professional= User.query.filter_by(professional_status= "Blacklisted").all()
    return professional

def curr_service_professional(service_id):
    professional= User.query.filter_by(service_id=service_id).all()
    return professional

def rating_professional(rating):    
    professional= User.query.filter_by(role=2,professional_rating=rating).all()
    return professional 
    
#all type of requests
def get_all_request():
    request= ServiceRequest.query.order_by(ServiceRequest.request_id.desc()).all()
    return request

def curr_user_request(curr_user):
    request= ServiceRequest.query.filter_by(user_id=curr_user.user_id).all()
    return request
def curr_professional_request(curr_user):
    request= curr_user.requested_from_professional
    return request

def curr_service_request(curr_service):
    request= curr_service.requests_for_services
    return request
    
# all types of services
def get_all_service():
    service= Service.query.order_by(Service.service_id.desc()).all()
    return service

def get_all_service_byrating():
    service= Service.query.order_by(Service.service_rating.desc()).all()
    return service
    
def get_all_service_byprice():
    service= Service.query.order_by(Service.price).all()
    return service

#def user_all_services(curr_user):
 #   service= curr_user.services
  #  return service
#def service_all_users(service):
 #   users= service.users
  #  return users
def service_all_professional(service):
    professional= User.query.filter_by(service_id=service.service_id).all()
    return professional
    


    
    
    
    
       

    

    

    
        
    
    

# general functionality

@app.route("/")
def homepage():
    return render_template("./basic_components/home.html")




@app.route("/login", methods=["POST","GET"])
def login():
    if request.method =="POST":
        user_name=request.form.get("user_name")
        password=request.form.get("password")
        user= User.query.filter_by(user_name=user_name).first()
        if user:
            if not cph(user.password,password):
                flash("Login Failed. Incorrect Password!!","danger")
                return redirect("/login")  
                
            session['id']= user.user_id
            result= wrong_access()
            if result:
                return result     
            user.user_status="Active"
            db.session.commit()
            flash("Login Successful!!","success")
            return redirect('/home')  
        else:
            flash("Login Failed.Incorrect UserName!!", "danger")
            return redirect("/login")                      
    
    return render_template("./basic_components/login.html")   



@app.route("/signup_professional", methods=["GET","POST"]) 
def signup_up():
    service=get_all_service()
    if request.method=="POST":
        user_name=request.form.get("user_name")
        password=request.form.get("password")
        encrypted_ps= gph(password)
        role=2
        address=request.form.get("address")
        pin_code=request.form.get("pin_code")
        service_id=request.form.get("service_id")
        user_status="Inactive"
        professional_status="Pending"
        name_user=request.form.get("name_user")
        file=request.files.get("file")
        user=User.query.filter_by(user_name=user_name).first()
        if not user:     
            new_user= User(user_name=user_name,name_user=name_user,password=encrypted_ps,role=role,address=address,pin_code=pin_code,service_id=service_id,user_status=user_status,professional_status=professional_status,professional_rating=0)
            db.session.add(new_user)
            db.session.commit()
            filename=f'{new_user.user_id}.pdf'   
            file.save(os.path.join("./static/files",filename))   
            flash("Sign up completed, you may login now.","success")
            return redirect("/login")
        flash("Username already exist!! Try logging in","danger")
        return redirect("/login")
    return render_template("signup_2.html",service=service)
        
        
        

@app.route("/signup_user", methods=["GET","POST"]) 
def signup_2():
   if request.method=="POST":
        user_name=request.form.get("user_name")
        password=request.form.get("password")
        if password.isdigit():
            flash("WEAK PASSWORD!! Try including some characters too","danger")
            return redirect("/signup")
        if password.isalpha():
            flash("WEAK PASSWORD!! Try including some digits too","danger")
            return redirect("/signup")
            
        
        
        encrypted_ps=gph(password)
        role=3
        name_user= request.form.get("name_user")
        address=request.form.get("address")
        pin_code=request.form.get("pin_code")
        user_status="Inactive"
        name_user=request.form.get("name_user")
        user=User.query.filter_by(user_name=user_name).first()
        if not user:      
            new_user= User(user_name=user_name,name_user=name_user,password=encrypted_ps,role=role,address=address,pin_code=pin_code,user_status=user_status)
            db.session.add(new_user)
            db.session.commit()
            flash("Sign up completed, you may login now.","success")
            return redirect("/login")
        flash("Username already exist!! Try logging in","danger")
        return redirect("/login")
   return render_template("signup_3.html")
    

@app.route("/logout")
def logout():
    curr_user=get_current_user()
    if curr_user:
        curr_user.user_status="Inactive"
        db.session.commit()
        session.pop('id', None)
        
        flash("You are logged out!!","success")
        return redirect("/login")
    else:
        flash("You are not logged in","danger")
        return redirect("/login")




@app.route("/home", methods=["GET","POST"])
@active
@professional_access
def home():
    curr_user= get_current_user()
    services= get_all_service()
    if curr_user :
        role=curr_user.role
        professional= get_pending_professional()
        request= get_all_request()
        if role==1:
          return render_template('1_home.html',curr_user=curr_user,services=services,professional=professional,request=request)
      
      
      
        if role==2:
           
           pending_request_all=ServiceRequest.query.filter_by(service_status="Pending",service_id=curr_user.service_id).order_by(ServiceRequest.request_id.desc()).all()
           rejected_requests= RejectedRequest.query.filter_by(professional_id=curr_user.user_id).all()
           pending_requests=[]
           rejected_id=[]
           for r in rejected_requests:
               rejected_id.append(r.request_id)
           for p in pending_request_all:
               if p.request_id not in rejected_id :
                   pending_requests.append(p)                    
               
           completed_requests=ServiceRequest.query.filter_by(professional_id=curr_user.user_id,service_status="Closed").order_by(ServiceRequest.request_id.desc()).all()
           active_requests=ServiceRequest.query.filter_by(professional_id=curr_user.user_id,service_status="Accepted").order_by(ServiceRequest.request_id.desc()).all()
           
           return render_template('2_home.html',pending_requests= pending_requests,curr_user=curr_user,completed_requests=completed_requests, active_requests=active_requests) 
       
       
        else:
            services= Service.query.order_by(Service.service_rating.desc()).all()
            request= ServiceRequest.query.filter_by(user_id=curr_user.user_id).all()
            active_requests= ServiceRequest.query.filter_by(user_id=curr_user.user_id, service_status="Accepted").order_by(ServiceRequest.request_id.desc()).all()
            completed_requests=ServiceRequest.query.filter_by(user_id=curr_user.user_id,service_status="Closed").order_by(ServiceRequest.request_id.desc()).all()
            pending_requests=ServiceRequest.query.filter_by(user_id=curr_user.user_id,service_status="Pending").order_by(ServiceRequest.request_id.desc()).all()
            
            return render_template('3_home.html',curr_user=curr_user,services=services,active_requests=active_requests, completed_requests=completed_requests,pending_requests=pending_requests)
                
    return redirect('/login')




@app.route("/delete", methods=["GET","POST"])
@check_access(1)
def delete():
    curr_user= get_current_user()
    
    session.pop['id',None]
    db.session.delete(curr_user)
    flash("Profile deleted", "success")  
    return redirect("/login")





#__________________________^^^^^^^^^^^^^^^^^^^^^^^^^^^____________________________#

#1) admin functionality with services


@app.route("/add_service", methods=["POST"])
@check_access(1)
def add_services():
    
    service_name= request.form.get("service_name")
    service_description= request.form.get("service_description")
    time_required= request.form.get("time_required")
    price=request.form.get("price")
    file=request.files.get("file")
    service=Service.query.filter_by(service_name=service_name).first()
    if service:
         flash("service already exist","danger")
         return redirect("/home")
    new_service=Service(service_name=service_name,service_description=service_description, price=price,time_required=time_required,service_rating=0)
    db.session.add(new_service)
    db.session.commit()
    filename = f'{new_service.service_id}.jpg'
    file.save (os.path.join("./static/service_images", filename)) 
    user= User.query.filter_by(service_id=new_service.service_id).all()
    for u in user:
        u.professional_status="Pending"
    flash("added successfully!","success")
    return redirect("/home")




@app.route("/update_service/<int:service_id>", methods=["POST"])
@check_access(1)
def update_service(service_id):
    
    if request.method=="POST":
        service=get_curr_service(service_id)
        if service:
            service_name=request.form.get("service_name")
            service_description=request.form.get("service_description")
            time_required=request.form.get("time_required")
            price=request.form.get("price")
            file=request.files.get("file")
            filename = f'{service.service_id}.jpg'
            file_path = os.path.join(f"./static/service_images", filename)
            
            if os.path.exists("file_path"):
                os.remove(file_path)
            
            file.save(file_path)
            
            service.service_name=service_name
            service.service_description=service_description
            service.time_required=time_required
            service.price=price
            db.session.commit()
            flash("Updated Successfully!!","success")
            return redirect("/home")
        flash("Id not found","danger")
        return("/home")
    



@app.route("/delete_service/<int:service_id>", methods=["GET"])
@check_access(1)
def delete_service(service_id):
    
    service= get_curr_service(service_id)
    if service_id:
            filename = f'{service.service_id}.jpg'
            file_path = os.path.join(f"./static/service_images", filename)
            service_request=ServiceRequest.query.filter_by(service_id=service_id).delete()
            db.session.delete(service)
            db.session.commit()
            
            
            if os.path.exists(file_path):
                os.remove(file_path)
            users=User.query.filter_by(service_id=service_id).all()
            for u in users:
                u.professional_status="Service_not_available"
            db.session.commit()
                
            
            
            
            flash("Deleted Successfully","success")  
            return redirect("/home") 
    flash("Service not found","danger")    
    return redirect("/home")
    




# 2)admin functionality with other users 


@app.route("/add_professional/<int:user_id>", methods=["GET"])
@check_access(1)
def add_professional(user_id):
    user=User.query.filter_by(user_id=user_id).first()
    user.professional_status="Accepted"
    db.session.commit()
    flash("Professional has been accepted", "success")
    return redirect("/home")
    
        
@app.route("/blacklist_professional/<int:user_id>", methods=["GET"])
@check_access(1)
def blacklist_user(user_id):

    user=User.query.filter_by(user_id=user_id).first()
    user.professional_status="Blacklisted"
    db.session.commit()
    flash("User has been blacklisted","success")
    return redirect("/home")


@app.route("/unblacklist_professional/<int:user_id>")
@check_access(1)
def unblock(user_id):
    user=User.query.filter_by(user_id=user_id).first()
    if user.role==2:
       user.professional_status="Pending"
       db.session.commit()
       flash("User has been Unblocked and is in pending","success")
       return redirect("/home")
    elif user.role==3:
        user.professional_status="Customer"   
        db.session.commit()
        flash("User has been unblocked","success")
        return redirect(f"/user_page/{user.user_id}")
    
    
    


# 3) professional functionality with accepting  and rejecting requests


@app.route("/accept_request/<int:request_id>/<int:professional_id>", methods=["GET","POST"])
@check_access(2)
@professional_access
def request_accepted(request_id,professional_id):
    check_access(2)
        
    request=ServiceRequest.query.filter_by(request_id=request_id).first()
    request.service_status="Accepted"
    request.professional_id=professional_id
    db.session.commit()
    flash("Service has been accepted","success")
    return redirect("/home")



@app.route("/reject_request/<int:request_id>/<int:professional_id>", methods=["GET","POST"])
@check_access(2)
@professional_access
def request_rejected(request_id,professional_id):
    
    rejected_request= RejectedRequest(request_id=request_id,professional_id=professional_id)
    db.session.add(rejected_request)
    db.session.commit()
    flash("Service has been rejected","danger")
    return redirect("/home")



#4) User functionality to book or close requests



@app.route("/book_service/<int:service_id>",methods=["POST"])
@check_access(3)
@professional_access
def book_service(service_id):
   
    curr_user=get_current_user()
    address=request.form.get("address")
    pin_code=request.form.get("pin_code")
    service= get_curr_service(service_id)
    requests= ServiceRequest(service_id=service_id,user_id=curr_user.user_id, service_name=service.service_name,user_name=curr_user.user_name,service_status="Pending",address=address,pin_code=pin_code,date_of_request=today,ratings=0,name_user=curr_user.name_user)
    db.session.add(requests)
    db.session.commit()
    flash("Service has been booked", "success")
    return redirect("/home")



@app.route("/completed_service/<int:request_id>",methods=["POST"])
@check_access(3)
@professional_access
def completed_request(request_id):

    ratings= int(request.form.get("rating"))
    remarks=request.form.get("service_remarks")
    requests=ServiceRequest.query.filter_by(request_id=request_id).first()
    service= get_curr_service(requests.service_id)
    professional= User.query.filter_by(user_id=requests.professional_id).first()
    
    tomorrow = today + timedelta(days=service.time_required)
    requests.service_status="Closed"
    requests.remarks=remarks
    requests.ratings=ratings   
    requests.date_of_completion=today
    db.session.commit()
    p_request=ServiceRequest.query.filter_by(professional_id=professional.user_id,service_status="Closed").count()
    professional.professional_rating=(ratings + professional.professional_rating)/p_request
    
    s_request= ServiceRequest.query.filter_by(service_id=service.service_id,service_status="Closed").count()
    service.service_rating= (ratings+service.service_rating)/s_request
    db.session.commit()
    flash("Service successfully completed", "success")
    
    return redirect("/home")

 
 
 
 #5) User and Service pages available for admin and individual summaries with graphs
 

def create_user_graph(x,y,user):
    import matplotlib
    matplotlib.use('Agg')

    import matplotlib.pyplot as plt

    y =y
    x =x

    plt.bar(x,y)
    plt.savefig(f'./static/charts_user/service_bargraph/{user.user_id}bar.jpg')
    plt.close() 
 
 
 
def create_service_graph(x,y,service):
    import matplotlib
    matplotlib.use('Agg')

    import matplotlib.pyplot as plt

    y =y
    x =x

    plt.bar(x,y)
    plt.savefig(f'./static/charts_service/service_bargraph/{service.service_id}bar.jpg')
    plt.close()  



def create_user_donut(x, y,user):
    import matplotlib
    matplotlib.use('Agg')

    import matplotlib.pyplot as plt
    
    if all(value == 0 for value in y):
      y = [0] * len(y)

    fig, ax = plt.subplots(figsize=(6, 6))

    startangle = 90

    # Plot the pie chart with the ratings
    ax.pie(y, labels=x, startangle=startangle, autopct='%1.1f%%', wedgeprops={'edgecolor': 'white', 'linewidth': 1, 'linestyle': 'solid'})

    # Add a white ring inside the pie chart
    ax.pie([1] * len(y), radius=0.7, colors=['white'] * len(y), startangle=startangle)

    plt.savefig(f'./static/charts_user/rating_pie/{user.user_id}pie.jpg')
    plt.close()


def create_service_donut(x, y,service):
    import matplotlib
    matplotlib.use('Agg')

    import matplotlib.pyplot as plt

    if all(value == 0 for value in y):
      y = [0] * len(y)

    fig, ax = plt.subplots(figsize=(6, 6))

    startangle = 90

    # Plot the pie chart with the ratings
    ax.pie(y, labels=x, startangle=startangle, autopct='%1.1f%%', wedgeprops={'edgecolor': 'white', 'linewidth': 1, 'linestyle': 'solid'})

    # Add a white ring inside the pie chart
    ax.pie([1] * len(y), radius=0.7, colors=['white'] * len(y), startangle=startangle)

    plt.savefig(f'./static/charts_service/rating_pie/{service.service_id}pie.jpg')
    plt.close() 
    
 
 
    

@app.route("/user_page/<int:user_id>")
@check_access(1)
@professional_access 
def user_page(user_id):
     curr_user=get_current_user()
     user=User.query.filter_by(user_id=user_id).first()
     n=0
     if user:
            if user.professional_status=="Blacklisted":
                n=1
            if user.professional_status=="Pending":
                n=2    
            if user.role==2:         
                requests=curr_professional_request(user)
                service_rejected=RejectedRequest.query.filter_by(professional_id=user_id).count()
                service_accepted= ServiceRequest.query.filter_by(professional_id=user_id,service_id=user.service_id,service_status="Accepted").count()
                service_closed= ServiceRequest.query.filter_by(professional_id=user_id,service_id=user.service_id,service_status="Closed").count()
                total=ServiceRequest.query.filter_by(professional_id=user.user_id).count()
                r0=ServiceRequest.query.filter_by(professional_id=user_id,service_id=user.service_id,service_status="Closed",ratings=0).count()
                r1=ServiceRequest.query.filter_by(professional_id=user_id,service_id=user.service_id,service_status="Closed",ratings=1).count()
                r2=ServiceRequest.query.filter_by(professional_id=user_id,service_id=user.service_id,service_status="Closed",ratings=2).count()
                r3=ServiceRequest.query.filter_by(professional_id=user_id,service_id=user.service_id,service_status="Closed",ratings=3).count()
                r4=ServiceRequest.query.filter_by(professional_id=user_id,service_id=user.service_id,service_status="Closed",ratings=4).count()
                r5=ServiceRequest.query.filter_by(professional_id=user_id,service_id=user.service_id,service_status="Closed",ratings=5).count()
                
                
                
                a=["Rating-0","Rating-1","Rating-2","Rating-3","Rating-4","Rating-5"]
                b=[r0,r1,r2,r3,r4,r5]     
                number=0
                for i in b:
                    if i==0:
                        number=number+1
                if number==6:
                    b[0]=1                  
                
                x=["service_accepted","service_rejected","service_completed"]
                y=[service_accepted,service_rejected,service_closed]     
                
                if user.professional_status!="Pending" and user.professional_status!="Blacklisted" :   
                  create_user_graph(x,y,user)
                  create_user_donut(a,b,user)
                return render_template("2_page.html",curr_user=curr_user,user=user,requests=requests,n=n,total=total)
            else:
                
                requests=curr_user_request(user)
                service_pending= ServiceRequest.query.filter_by(user_id=user.user_id,service_status="Pending").count()
                service_accepted=ServiceRequest.query.filter_by(user_id=user.user_id,service_status="Accepted").count()
                service_closed= ServiceRequest.query.filter_by(user_id=user.user_id,service_status="Closed").count()
                total=ServiceRequest.query.filter_by(user_id=user.user_id).count()
                r0=ServiceRequest.query.filter_by(user_id=user.user_id,service_status="Closed",ratings=0).count()
                r1=ServiceRequest.query.filter_by(user_id=user.user_id,service_status="Closed",ratings=1).count()
                r2=ServiceRequest.query.filter_by(user_id=user.user_id,service_status="Closed",ratings=2).count()
                r3=ServiceRequest.query.filter_by(user_id=user.user_id,service_status="Closed",ratings=3).count()
                r4=ServiceRequest.query.filter_by(user_id=user.user_id,service_status="Closed",ratings=4).count()
                r5=ServiceRequest.query.filter_by(user_id=user.user_id,service_status="Closed",ratings=5).count()
                
                a=["Rating-0","Rating-1","Rating-2","Rating-3","Rating-4","Rating-5"]
                b=[r0,r1,r2,r3,r4,r5]
                number=0
                for i in b:
                    if i==0:
                        number=number+1
                if number==6:
                    b[0]=1
                
                x=["service_accepted","service_pending","service_completed"]
                y=[service_accepted,service_pending,service_closed] 
                if user.professional_status!="Pending" and user.professional_status!="Blacklisted" :  
                  create_user_graph(x,y,user)
                  create_user_donut(a,b,user)
                
                return render_template("3_page.html",curr_user=curr_user,user=user,requests=requests,n=n,total=total)
     else:
         flash("This user does not exist","danger")
         return redirect("/home")

 
# summary page


@app.route("/summary")
@active
@professional_access
def summary():
            curr_user= get_current_user()
            if curr_user:
                if curr_user.role==1:
                        
                        r0=ServiceRequest.query.filter_by(service_status="Closed",ratings=0).count()
                        r1=ServiceRequest.query.filter_by(service_status="Closed",ratings=1).count()
                        r2=ServiceRequest.query.filter_by(service_status="Closed",ratings=2).count()
                        r3=ServiceRequest.query.filter_by(service_status="Closed",ratings=3).count()
                        r4=ServiceRequest.query.filter_by(service_status="Closed",ratings=4).count()
                        r5=ServiceRequest.query.filter_by(service_status="Closed",ratings=5).count()
                        
                        service_pending= ServiceRequest.query.filter_by(service_status="Pending").count()
                        service_accepted=ServiceRequest.query.filter_by(service_status="Accepted").count()
                        service_closed= ServiceRequest.query.filter_by(service_status="Closed").count()
                        total_request=ServiceRequest.query.count()
                        total_professional=User.query.filter_by(role=2).count()
                        total_customer=User.query.filter_by(role=3).count()
                        total_service=User.query.filter_by(role=2).count()
                        
                        
                        a=["Rating-0","Rating-1","Rating-2","Rating-3","Rating-4","Rating-5"]
                        b=[r0,r1,r2,r3,r4,r5]
                        number=0
                        for i in b:
                            if i==0:
                                number=number+1
                        if number==6:
                            b[0]=1        

                        x=["service_accepted","service_pending","service_completed"]
                        y=[service_accepted,service_pending,service_closed]
                        
                        create_user_graph(x,y,curr_user)
                        create_user_donut(a,b,curr_user) 
                        return render_template("1_summary.html",curr_user=curr_user,total_request=total_request,total_service=total_service,total_customer=total_customer,total_professional=total_professional)
                        
                    
                if curr_user.role==2:
                           
                    requests=curr_professional_request(curr_user)
                    service= get_curr_service(curr_user.service_id)
                    service_rejected=RejectedRequest.query.filter_by(professional_id=curr_user.user_id).count()
                    service_accepted= ServiceRequest.query.filter_by(professional_id=curr_user.user_id,service_status="Accepted").count()
                    service_closed= ServiceRequest.query.filter_by(professional_id=curr_user.user_id,service_status="Closed").count()
                    total_request=ServiceRequest.query.filter_by(professional_id=curr_user.user_id).count()
                    r0=ServiceRequest.query.filter_by(professional_id=curr_user.user_id,service_id=curr_user.service_id,service_status="Closed",ratings=0).count()
                    r1=ServiceRequest.query.filter_by(professional_id=curr_user.user_id,service_id=curr_user.service_id,service_status="Closed",ratings=1).count()
                    r2=ServiceRequest.query.filter_by(professional_id=curr_user.user_id,service_id=curr_user.service_id,service_status="Closed",ratings=2).count()
                    r3=ServiceRequest.query.filter_by(professional_id=curr_user.user_id,service_id=curr_user.service_id,service_status="Closed",ratings=3).count()
                    r4=ServiceRequest.query.filter_by(professional_id=curr_user.user_id,service_id=curr_user.service_id,service_status="Closed",ratings=4).count()
                    r5=ServiceRequest.query.filter_by(professional_id=curr_user.user_id,service_id=curr_user.service_id,service_status="Closed",ratings=5).count()
                    
                    
                    
                    a=["Rating-0","Rating-1","Rating-2","Rating-3","Rating-4","Rating-5"]
                    b=[r0,r1,r2,r3,r4,r5]
                    
                    number=0
                    for i in b:
                        if i==0:
                                number=number+1
                    if number==6:
                         b[0]=1
                    
                    x=["service_accepted","service_rejected","service_completed"]
                    y=[service_accepted,service_rejected,service_closed]         
                    create_user_graph(x,y,curr_user)
                    create_user_donut(a,b,curr_user)
                    return render_template("2_summary.html",curr_user=curr_user,requests=requests,total_request=total_request,service=service,service_closed=service_closed)
                
                
                elif curr_user.role==3:                                        
                    
                    requests=curr_user_request(curr_user)
                    
                    service_pending= ServiceRequest.query.filter_by(user_id=curr_user.user_id,service_status="Pending").count()
                    service_accepted=ServiceRequest.query.filter_by(user_id=curr_user.user_id,service_status="Accepted").count()
                    service_closed= ServiceRequest.query.filter_by(user_id=curr_user.user_id,service_status="Closed").count()
                    total_request=ServiceRequest.query.filter_by(user_id=curr_user.user_id).count()

                    r0=ServiceRequest.query.filter_by(user_id=curr_user.user_id,service_status="Closed",ratings=0).count()
                    r1=ServiceRequest.query.filter_by(user_id=curr_user.user_id,service_status="Closed",ratings=1).count()
                    r2=ServiceRequest.query.filter_by(user_id=curr_user.user_id,service_status="Closed",ratings=2).count()
                    r3=ServiceRequest.query.filter_by(user_id=curr_user.user_id,service_status="Closed",ratings=3).count()
                    r4=ServiceRequest.query.filter_by(user_id=curr_user.user_id,service_status="Closed",ratings=4).count()
                    r5=ServiceRequest.query.filter_by(user_id=curr_user.user_id,service_status="Closed",ratings=5).count()
                    
                    a=["Rating-0","Rating-1","Rating-2","Rating-3","Rating-4","Rating-5"]
                    b=[r0,r1,r2,r3,r4,r5]
                    
                    n=0
                    for i in b:
                        if i==0:
                             n=n+1
                    if n==6:
                        b[0]=1
                    
                    x=["service_accepted","service_pending","service_completed"]
                    y=[service_accepted,service_pending,service_closed] 
                    
                    create_user_graph(x,y,curr_user)
                    create_user_donut(a,b,curr_user)
                    
                    return render_template("3_summary.html",curr_user=curr_user,requests=requests,total_request=total_request)
                
                else:
                    flash("There is some problem. Try again","danger")
                    return redirect("/login")
                
            else:
                flash("You are not logged in. Try logging in ","danger")
                return redirect("/login")



           
#Service page for admin access


@app.route("/service_page/<int:service_id>")
@check_access(1)
def service_page(service_id):
     
     curr_user= get_current_user()
     service=get_curr_service(service_id)
     if service:
        professional=service_all_professional(service)
        requests=curr_service_request(service) 
        
        service_pending= ServiceRequest.query.filter_by(service_id=service_id,service_status="Pending").count()
        service_accepted=ServiceRequest.query.filter_by(service_id=service_id,service_status="Accepted").count()
        service_closed= ServiceRequest.query.filter_by(service_id=service_id,service_status="Closed").count()
        total_request=ServiceRequest.query.filter_by(service_id=service_id).count()
        total_professional=User.query.filter_by(service_id=service_id).count()
            
        r0=ServiceRequest.query.filter_by(service_id=service_id,service_status="Closed",ratings=0).count()
        r1=ServiceRequest.query.filter_by(service_id=service_id,service_status="Closed",ratings=1).count()
        r2=ServiceRequest.query.filter_by(service_id=service_id,service_status="Closed",ratings=2).count()
        r3=ServiceRequest.query.filter_by(service_id=service_id,service_status="Closed",ratings=3).count()
        r4=ServiceRequest.query.filter_by(service_id=service_id,service_status="Closed",ratings=4).count()
        r5=ServiceRequest.query.filter_by(service_id=service_id,service_status="Closed",ratings=5).count()
        
        a=["Rating-0","Rating-1","Rating-2","Rating-3","Rating-4","Rating-5"]
        b=[r0,r1,r2,r3,r4,r5]
        
        n=0
        for i in b:
            if i==0:
                n=n+1
        if n==6:
            b[0]=1
        
        x=["service_accepted","service_pending","service_completed"]
        y=[service_accepted,service_pending,service_closed]
        create_service_graph(x,y,service)
        create_service_donut(a,b,service)
        
        return render_template("service_page.html",curr_user=curr_user,requests=requests,total_request=total_request,service=service,professional=professional,total_professional=total_professional)
     else:
         flash("Service does not exist","danger")
         return redirect("/home")
     


# 6) search functionality 



@app.route("/search", methods=["GET","POST"])
@active
@professional_access
def admin_search():
    curr_user=get_current_user()
    if curr_user:
        
#for admin         
        if curr_user.role==1:
            requests=get_all_request()
            service=get_all_service()
            professional=get_all_professional()
            customer= User.query.filter_by(role=3,).all()
            user= list(set(professional).union(set(customer)))
            search_key=request.args.get("search_key")
            if search_key=="None":
                search_key=None
                           
            ordered= request.args.get("ordered")
            filtered=request.args.get("filtered")
            find= request.args.get("find")
            
            if request.method=="POST":
                search_key= request.form.get("search_key")
                ordered=None
                filtered=None
                find=None
            
            
            if search_key:
                request_servicename= ServiceRequest.query.filter(ServiceRequest.service_name.contains(search_key)).all()
                request_professionalid=ServiceRequest.query.filter(ServiceRequest.professional_id.contains(search_key)).all()
                request_username=ServiceRequest.query.filter(ServiceRequest.user_name.contains(search_key)).all()
                request_address=ServiceRequest.query.filter(ServiceRequest.address.contains(search_key)).all()
                request_pincode=ServiceRequest.query.filter(ServiceRequest.pin_code.contains(search_key)).all()
                
                some_requests=list(set(request_servicename).union(set(request_professionalid)).union(set(request_username)).union(set(request_address)).union(set(request_pincode)))
                
                if filtered=="closed" :
                      requests=[]
                      for r in some_requests:
                          if  r.service_status=="Closed":
                                     requests.append(r) 
                elif filtered=="active" :
                    requests=[]
                    for r in some_requests:
                       if  r.service_status=="Accepted":
                            requests.append(r)
                
                elif filtered=="pending" :
                   requests=[]
                   for r in some_requests:
                        if  r.service_status=="Pending":
                               requests.append(r)
                else :
                
                   requests=[]
                    
                   for r in some_requests:
                      requests.append(r) 
                
                
                name_service= Service.query.filter(Service.service_name.contains(search_key)).all()
                time_service= Service.query.filter(Service.time_required.contains(search_key)).all()
                desc_service= Service.query.filter(Service.service_description.contains(search_key)).all()
                some_service = list(set(name_service).union(set(time_service)).union(set(desc_service))) 
                ids=[]
                for s in some_service:
                    ids.append(s.service_id)
                    
                if ordered=="price" :
                      aservice= get_all_service_byprice()
                      service=[]
                      for s in aservice:
                          if s.service_id in ids:
                              service.append(s)
                              
                        
                elif ordered=="rating" :
                    aservice=get_all_service_byrating()
                    service=[]
                    for s in aservice:
                        if s.service_id in ids:
                              service.append(s)
              
                
                else :
                    aservice=get_all_service()
                    service=[]
                    for s in aservice:
                        if s.service_id in ids:
                              service.append(s)
                
                
                name_user=User.query.filter(User.name_user.contains(search_key)).all()
                service_user=User.query.filter(User.service_id.contains(search_key)).all()
                address_user=User.query.filter(User.address.contains(search_key)).all()
                pincode_user=User.query.filter(User.pin_code.contains(search_key)).all()
                uname_user=User.query.filter(User.user_name.contains(search_key)).all()
                rating_user=User.query.filter(User.professional_rating.contains(search_key)).all()               
                
                some_user= list(set(name_user).union(set(service_user)).union(set(address_user)).union(set(pincode_user)).union(set(uname_user)).union(set(rating_user)))
                ids=[]
                for i in some_user:
                    ids.append(i.user_id)
                
                if find=="professional":
                    professional= User.query.filter_by(role=2).all()
                    user=[]
                    for i in professional:
                        if i.user_id in ids:
                            user.append(i)
                            
                elif find=="customer":
                    customer= User.query.filter_by(role=3).all()
                    user=[]
                    for i in customer:
                        if i.user_id in ids:
                            user.append(i)
                    
                elif find=="blacklist":
                    blacklist= User.query.filter_by(professional_status='Blacklisted').all()
                    user=[]
                    for i in blacklist:
                        if i.user_id in ids:
                            user.append(i)
                elif find=="pending":
                    pending= User.query.filter_by(professional_status='Pending').all()
                    user=[]
                    for i in pending:
                        if i.user_id in ids:
                            user.append(i)
                else:
                    alls= User.query.filter(User.role!=1).all()
                    user=[]
                    for i in alls:
                        if i.user_id in ids:
                            user.append(i)
                
                               
                
            else:
                if filtered== "pending":
                    requests= ServiceRequest.query.filter_by( service_status="Pending").all()
                elif filtered== "active":
                    requests= ServiceRequest.query.filter_by( service_status="Accepted").all()                   
                elif filtered== "closed":
                    requests= ServiceRequest.query.filter_by( service_status="Closed").all() 
                else:
                    requests= ServiceRequest.query.all()  
                         
                if ordered=="price":
                    service= get_all_service_byprice()
                        
                elif ordered=="rating" :
                    service=get_all_service_byrating()
                else :
                    service=get_all_service()
                
                               
                
                if find=="professional":
                    user= User.query.filter_by(role=2).all()
                            
                elif find=="customer":
                    user= User.query.filter_by(role=3).all()
                    
                elif find=="blacklist":
                    user= User.query.filter_by(professional_status='Blacklisted').all()
                    
                elif find=="pending":
                    user= User.query.filter_by(professional_status='Pending').all()
                    
                else:
                    user= User.query.filter(User.role!=1).all()
                    
                    
                
                
                
            return render_template("1_search.html",curr_user=curr_user,user=user,requests=requests,service=service,search_key=search_key)  
            
        
# professional search functionality        
        elif curr_user.role==2:
            
            curr_user=get_current_user()
            requests=curr_professional_request(curr_user)
            search_key= request.args.get("search_key")
            if search_key=="None":
                search_key=None
            filtered= request.args.get("filtered")
            
            if request.method=="POST":
                search_key= request.form.get("search_key")
                filtered=None
            
            if search_key and filtered =="closed" : 
                name_requests= ServiceRequest.query.filter(ServiceRequest.name_user.contains(search_key)).all()
                address_requests= ServiceRequest.query.filter(ServiceRequest.address.contains(search_key)).all()
                pin_code_requests= ServiceRequest.query.filter(ServiceRequest.pin_code.contains(search_key)).all()
                
                some_requests = list(set(name_requests).union(set(address_requests)).union(set(pin_code_requests))) 
                requests=[]
                for r in some_requests:
                    if r.professional_id==curr_user.user_id and r.service_status=="Closed":
                        requests.append(r)
                
                
            elif search_key and filtered =="active" : 
                name_requests= ServiceRequest.query.filter(ServiceRequest.name_user.contains(search_key)).all()
                address_requests= ServiceRequest.query.filter(ServiceRequest.address.contains(search_key)).all()
                pin_code_requests= ServiceRequest.query.filter(ServiceRequest.pin_code.contains(search_key)).all()
                
                some_requests = list(set(name_requests).union(set(address_requests)).union(set(pin_code_requests)))  
                requests=[]
                for r in some_requests:
                    if r.professional_id==curr_user.user_id and r.service_status=="Accepted":
                        requests.append(r)  
            
            elif filtered=="closed":
                requests= ServiceRequest.query.filter_by(professional_id=curr_user.user_id,service_status="Closed").all()
            elif filtered=="active":
                requests= ServiceRequest.query.filter_by(professional_id=curr_user.user_id,service_status="Accepted").all()
                    
            elif search_key:
                name_requests= ServiceRequest.query.filter(ServiceRequest.name_user.contains(search_key)).all()
                address_requests= ServiceRequest.query.filter(ServiceRequest.address.contains(search_key)).all()
                pin_code_requests= ServiceRequest.query.filter(ServiceRequest.pin_code.contains(search_key)).all()
                
                some_requests = list(set(name_requests).union(set(address_requests)).union(set(pin_code_requests)))
                requests=[]
                for r in some_requests:
                    if r.professional_id==curr_user.user_id:
                        requests.append(r)           
    
            
            return render_template("2_search.html",curr_user=curr_user,requests=requests, search_key=search_key) 

#customer search functionality        
        else:
    
            curr_user=get_current_user()
            service=get_all_service_byrating()
            requests=curr_user_request(curr_user)
            search_key=request.args.get("search_key")
            if search_key=="None":
                search_key=None
            filtered= request.args.get("filtered")
            ordered= request.args.get("ordered")
            
            if request.method=="POST":
                search_key= request.form.get("search_key")
                filtered=None
                ordered=None
            
            if search_key :
                name_requests= ServiceRequest.query.filter(ServiceRequest.service_name.contains(search_key)).all()
                address_requests= ServiceRequest.query.filter(ServiceRequest.address.contains(search_key)).all()
                profess_requests= ServiceRequest.query.filter(ServiceRequest.professional_id.contains(search_key)).all()
                some_requests = list(set(name_requests).union(set(address_requests)).union(set(profess_requests))) 
                
                if filtered=="closed" :
                      requests=[]
                      for r in some_requests:
                          if r.user_id==curr_user.user_id and r.service_status=="Closed":
                                     requests.append(r) 
                elif filtered=="active" :
                    requests=[]
                    for r in some_requests:
                       if r.user_id==curr_user.user_id and r.service_status=="Accepted":
                            requests.append(r)
                
                elif filtered=="pending" :
                   requests=[]
                   for r in some_requests:
                        if r.user_id==curr_user.user_id and r.service_status=="Pending":
                               requests.append(r)
                else :
                
                   requests=[]
                    
                   for r in some_requests:
                      if r.user_id==curr_user.user_id :
                            requests.append(r)              
                 
                name_service= Service.query.filter(Service.service_name.contains(search_key)).all()
                time_service= Service.query.filter(Service.time_required.contains(search_key)).all()
                desc_service= Service.query.filter(Service.service_description.contains(search_key)).all()
                some_service = list(set(name_service).union(set(time_service)).union(set(desc_service))) 
                ids=[]
                for s in some_service:
                    ids.append(s.service_id)
                    
                if ordered=="price" :
                      aservice= get_all_service_byprice()
                      service=[]
                      for s in aservice:
                          if s.service_id in ids:
                              service.append(s)
                              
                        
                elif ordered=="newest" :
                    aservice=get_all_service()
                    service=[]
                    for s in aservice:
                        if s.service_id in ids:
                              service.append(s)
              
                
                else :
                    aservice=get_all_service_byrating()
                    service=[]
                    for s in aservice:
                        if s.service_id in ids:
                              service.append(s)
                              
            else:
                if filtered== "pending":
                    requests= ServiceRequest.query.filter_by(user_id=curr_user.user_id, service_status="Pending").all()
                elif filtered== "active":
                    requests= ServiceRequest.query.filter_by(user_id=curr_user.user_id, service_status="Accepted").all()                   
                elif filtered== "closed":
                    requests= ServiceRequest.query.filter_by(user_id=curr_user.user_id, service_status="Closed").all() 
                else:
                    requests= ServiceRequest.query.filter_by(user_id=curr_user.user_id).all()  
                         
                if ordered=="price":
                    service= get_all_service_byprice()
                        
                elif ordered=="newest" :
                    service=get_all_service()
                else :
                    service=get_all_service_byrating()    
                
                
                
            
            return render_template("3_search.html",curr_user=curr_user,requests=requests, search_key=search_key, service=service)
   
    else:
        flash("You are not logged in. Try logging in","danger")
        return redirect("/login")






















