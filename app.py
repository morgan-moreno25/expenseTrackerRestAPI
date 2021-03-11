from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from db import db
from blacklist import BLACKLIST

from resources.auth import UserLogin, UserRegister, UserLoad, UserLogout
from resources.user import User, UserList
from resources.income import Income, IncomeList
from resources.expense import Expense, ExpenseList


app = Flask(__name__)
api = Api(app, prefix='/api')

# App configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'dev'
app.config['JWT_HEADER_TYPE'] = 'JWT'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {
        'message': 'This token has expired',
        'error': 'token_expired',
    }, 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return {
        'message': 'No token provided',
        'error': 'authorization_required',
    }, 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return {
        'message': 'Token has been revoked',
        'error': 'token_revoked',
    }, 401


@jwt.user_identity_loader
def load_identity(payload):
    return {
        'user_id': payload.id,
        'username': payload.username
    }


@app.before_first_request
def create_tables():
    db.create_all()


# Auth Routes
api.add_resource(UserLogin, '/auth/login')
api.add_resource(UserRegister, '/auth/register')
api.add_resource(UserLoad, '/auth/user')
api.add_resource(UserLogout, '/auth/logout')

# User Routes
api.add_resource(User, '/users/<int:_id>')
api.add_resource(UserList, '/users')

# Income Routes
api.add_resource(Income, '/income/<int:_id>')
api.add_resource(IncomeList, '/income')

# Expense Routes
api.add_resource(Expense, '/expenses/<int:_id>')
api.add_resource(ExpenseList, '/expenses')

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=3001, debug=True)
