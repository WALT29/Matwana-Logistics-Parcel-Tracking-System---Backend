from models import User,db
from flask import Blueprint,request,make_response
from werkzeug.security import generate_password_hash,check_password_hash
from flask_restful import Api, Resource

auth_bp = Blueprint('auth_bp',__name__, url_prefix='/auth')
api=Api(auth_bp)

class Signup(Resource):
    def post:
        