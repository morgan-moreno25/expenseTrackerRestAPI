from flask_restful import Resource, reqparse
from models.user import UserModel
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
)
from blacklist import BLACKLIST

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, required=True, help='Username is required')
user_parser.add_argument('password', type=str, required=True, help='Password is required')


class UserLogin(Resource):
    def post(self):
        data = user_parser.parse_args()

        if not UserModel.find_by_username(data['username']):
            return {
                       "message": "User does not exist",
                       "error": "invalid_credentials",
                   }, 401

        user = UserModel.find_by_username(data['username'])

        if check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=user)

            return {
                "access_token": access_token,
                "user": user.json()
            }, 200
        else:
            return {
                "message": "Password is invalid",
                "error": "invalid_credentials"
            }, 401


class UserRegister(Resource):
    def post(self):
        data = user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {
                'message': 'User already exists',
                'error': 'validation_error'
            }, 400
        else:
            password_hash = generate_password_hash(data['password'], salt_length=10)
            user = UserModel(data['username'], password_hash)
            user.save_to_db()
            access_token = create_access_token(identity=user)

            return {
                'access_token': access_token,
                'user': user.json(),
            }, 201


class UserLoad(Resource):

    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        user = UserModel.find_by_id(identity['user_id'])
        return {
            'user': user.json(),
        }, 200


class UserLogout(Resource):

    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        BLACKLIST.add(jti)
        return {
            'message': 'Successfully logged out'
        }, 200
