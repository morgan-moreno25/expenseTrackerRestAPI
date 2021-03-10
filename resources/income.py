from flask_restful import Resource, reqparse
from models.income import IncomeModel
from flask_jwt_extended import get_jwt_identity, jwt_required

income_parser = reqparse.RequestParser()
income_parser.add_argument('category', type=str, required=True, help='Category is required')
income_parser.add_argument('amount', type=float, required=True, help='Amount is required')


class Income(Resource):

    @jwt_required()
    def put(self, _id):
        data = income_parser.parse_args()

        current_user = get_jwt_identity()

        income = IncomeModel.find_by_id(_id)

        if income:
            if income.user_id == current_user['user_id']:
                income.category = data['category']
                income.amount = data['amount']
                income.save_to_db()
            else:
                return {
                           'message': 'You are not authorized to update this income data',
                           'error': 'not_authorized'
                       }, 401
        else:
            income = IncomeModel(data['category'], data['amount'], current_user['user_id'])
            income.save_to_db()

        return {
                   'message': 'Succesfully updated',
                   'updatedIncome': income.json()
               }, 200

    @jwt_required()
    def delete(self, _id):
        current_user = get_jwt_identity()

        income = IncomeModel.find_by_id(_id)

        if income:
            if income.user_id == current_user['user_id']:
                if income:
                    income.delete_from_db()
            else:
                return {
                           'message': 'You are not authorized to delete this income data',
                           'error': 'not_authorized'
                       }, 401
        else:
            return {
                       'message': f'Income data with id {_id} does not exist',
                       'error': 'bad_request'
                   }, 400

        return {
                   'message': 'Succesfully deleted',
               }, 200


class IncomeList(Resource):

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()

        try:
            income = IncomeModel.get_all_by_user(current_user['user_id'])
        except:
            return {
                       'message': 'An error occurred when fetching the income data',
                       'error': 'server_error'
                   }, 500

        return {
                   'income': [i.json() for i in income]
               }, 200

    @jwt_required()
    def post(self):
        data = income_parser.parse_args()

        current_user = get_jwt_identity()

        income = IncomeModel(data['category'], data['amount'], current_user['user_id'])

        try:
            income.save_to_db()
        except:
            return {
                       'message': 'An error occurred when saving the income data to the database',
                       'error': 'server_error'
                   }, 500

        return {
                   'income': income.json()
               }, 201
