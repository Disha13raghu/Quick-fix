from backend.models import User,Service
from backend.database import db
from werkzeug.security import generate_password_hash as gph
from werkzeug.security import check_password_hash as cph
from app import app


services= [("Kitchen Cleaning","Cleaning and degreasing kitchen surfaces, appliances, and sinks",2,500,0),
           ("Electrical Repairs","Troubleshooting and fixing electrical problems, installing lights or fans, and ensuring safe wiring",1,700,0),
           ("Gardening Services","Lawn care, planting, trimming, and maintenance of gardens or indoor plants.",4,300,0),
           ("Sofa and Carpet Cleaning","Specialized cleaning services for upholstery and carpets to remove dirt, stains, and allergens",3,900,0),]





Admin=[(1,"admin@gmail.com",gph("admin"),"Inactive")]
Customers=[(3,"customer1@gmail.com",gph("customer1"),"Mystic Falls","11111","Inactive","customer1"),
           (3,"customer2@gmail.com",gph("customer2"),"Beverly Hills","2222","Inactive","customer2"),
           (3,"customer3@gmail.com",gph("customer3"),"Never Land","3333","Inactive","customer3"),
           (3,"customer4@gmail.com",gph("customer4"),"New Orleans","1313","Inactive","customer4")]

Professionals=[(2,"professional1@gmail.com",gph("professional1"),"Lily Gardens","111",1,"Inactive","Pending",0,"professional1"),
               (2,"professional2@gmail.com",gph("professional2"),"Green Gables","113",2,"Inactive","Pending",0,"professional2"),
               (2,"professional3@gmail.com",gph("professional3"),"Silicon City","123",3,"Inactive","Pending",0,"professional3"),
               (2,"professional4@gmail.com",gph("professional4"),"Rainland","133",1,"Inactive","Pending",0,"professional4"),
               (2,"professional5@gmail.com",gph("professional5"),"Kelly Island","124",3,"Inactive","Pending",0,"professional5")]


for sn,sd,tr,p,sr in services:
            service= Service(service_name=sn,service_description=sd,time_required=tr,price=p,service_rating=sr)
            db.session.add(service)
db.session.commit()



for r,un,ps,us in Admin:
            user= User(role=r,user_name=un,password=ps,user_status=us)
            db.session.add(user)
db.session.commit()



for r,un,ps,ad,pc,us,nu  in Customers:
            user= User(role=r,user_name=un,password=ps,address=ad,pin_code=pc,user_status=us,name_user=nu)
            db.session.add(user)
db.session.commit()
 
 
            
for r,un,ps,ad,pc,s,us,pst,pr,nu in Professionals:
            user= User(role=r,user_name=un,password=ps,address=ad,pin_code=pc,service_id=s,user_status=us,professional_status=pst,professional_rating=pr,name_user=nu)
            db.session.add(user)
db.session.commit()        

