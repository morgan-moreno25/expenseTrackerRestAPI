from flask_restful import Resource, reqparse
from models.user import UserModel
from flask_jwt_extended import get_jwt_identity, jwt_required

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, required=True, help='Username is required')
user_parser.add_argument('password', type=str, required=True, help='Password is required')


class User(Resource):

    @jwt_required
    def put(self, _id):
        data = user_parser.parse_args()

        current_user = get_jwt_identity()

        if current_user['user_id'] == _id:
            user = UserModel.find_by_id(_id)

            if user:
                user.username = data['username']
                user.password = data['password']
                user.save_to_db()

            else:
                user = UserModel(**data)
                user.save_to_db()

            return {
                       'updatedUser': user.json()
                   }, 200
        else:
            return {
                       'message': 'You are not authorized to update this user',
                       'error': 'not_authorized'
                   }, 401

    @jwt_required
    def delete(self, _id):
        current_user = get_jwt_identity()

        if current_user['user_id'] == _id:

            user = UserModel.find_by_id(_id)

            if user:
                user.delete_from_db()

            return {
                       'message': 'Successfully deleted'
                   }, 200

        else:
            return {
                       'message': 'You are not authorized to delete this user',
                       'error': 'not_authorized',
                   }, 401


class UserList(Resource):

    def get(self):
        users = UserModel.get_all()
        return {
            'users': [user.json() for user in users]
        }
