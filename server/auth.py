from models import User,db
from flask import Blueprint,request,make_response
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token,create_refresh_token,JWTManager,get_jwt_identity,jwt_required,get_jwt
from functools import wraps

jwt=JWTManager()

auth_bp = Blueprint('auth_bp',__name__, url_prefix='/auth')
api=Api(auth_bp)



def allow(required_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            jwt_claims=get_jwt()
            user_role=jwt_claims.get('role',None)
            
            if user_role not in required_roles:
                return make_response({
                    "error":"Access forbidden"
                },403)
            return func(*args,**kwargs)
        return wrapper
    return decorator

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

class Login(Resource):
    def post(self):
        data=request.get_json()
        phone_number=data['phone_number']
        password=data['password']
        
        user=User.get_user_by_phone(phone_number=phone_number)
        
        
        if user and (user.check_password(password=password)):
            access_token=create_access_token(identity=user.id,additonal_claims={"role":user.role})
            refresh_token=create_refresh_token(identity=user.id)
            
            return make_response({
                "message":"logged in successfully",
                "tokens":{
                    "access_token":access_token,
                    "refresh_token":refresh_token
                }
            },200)
        
        else:
            return make_response({
                "message":"Invalid username or password"
            },400)

api.add_resource(Login,'/login')
api.add_resource(Signup,'/signup')
        
        