from models import User,db
from flask import Blueprint,request,make_response
from werkzeug.security import generate_password_hash,check_password_hash
from flask_restful import Api, Resource

auth_bp = Blueprint('auth_bp',__name__, url_prefix='/auth')
api=Api(auth_bp)

class Signup(Resource):
    def post(self):
        data=request.get_json()
        name=data['name']
        phone_number=data['phone_number']
        email=data['email']
        password=data['password']
        role=data['role']
        
        errors=[]
        if len(name)<2:
            errors.append("Name is required and name should be at least 3 characters")
        if not phone_number.isdigit() or not len(phone_number) ==10:
            errors.append('Phone number should be 10 characters and have digits only')
        if not "@" in email or not email:
            errors.append('email is required')
        if len(password) <8 :
            errors.append('Password should be at least 8 characters')
        
        user =User.get_user_by_name(name=name)
        
        if user is not None:
            errors.append("User with that username exists")
        
        if errors:
            return make_response({
                "errors":errors
            },400)
            
        new_user=User(name=name,
                      phone_number=phone_number,
                      email=email,
                      role=role)
        
        new_user.set_password(password=password)
        new_user.save()
        
        return make_response({
            "name":name,
            "phone_number":phone_number,
            "password":password
        },201)
        
api.add_resource(Signup,'/signup')
        
        