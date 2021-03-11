from flask_restful import Resource, reqparse
from models.expense import ExpenseModel
from flask_jwt_extended import get_jwt_identity, jwt_required

expense_parser = reqparse.RequestParser()
expense_parser.add_argument('date', type=str, required=True, help='Date is required')
expense_parser.add_argument('category', type=str, required=True, help='Category is required')
expense_parser.add_argument('amount', type=float, required=True, help='Amount is required')


class Expense(Resource):

    @jwt_required()
    def put(self, _id):
        data = expense_parser.parse_args()
        current_user = get_jwt_identity()

        expense = ExpenseModel.find_by_id(_id)

        if expense:
            if expense.user_id == current_user['user_id']:
                expense.date = data['date']
                expense.category = data['category']
                expense.amount = data['amount']
                expense.save_to_db()
            else:
                return {
                           'message': 'You are not authorized to update this expense data',
                           'error': 'not_authorized'
                       }, 401
        else:
            expense = ExpenseModel(data['date'], data['category'], data['amount'], current_user['user_id'])
            expense.save_to_db()

        return {
                   'message': 'Successfully updated',
                   'updatedExpense': expense.json()
               }, 200

    @jwt_required()
    def delete(self, _id):
        current_user = get_jwt_identity()

        expense = ExpenseModel.find_by_id(_id)

        if expense:
            if expense.user_id == current_user['user_id']:
                expense.delete_from_db()
            else:
                return {
                           'message': 'You are not authorized to delete this expense data',
                           'error': 'not_authorized'
                       }, 401
        else:
            return {
                       'message': f'Expense data with id {_id} does not exist',
                       'error': 'bad_request'
                   }, 400

        return {
                   'message': 'Successfully deleted',
               }, 200


class ExpenseList(Resource):

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()

        try:
            expenses = ExpenseModel.get_all_by_user(current_user['user_id'])
        except:
            return {
                       'message': 'An error occurred while fetching expenses from the database',
                       'error': 'server_error',
                   }, 500

        return {
                   'expenses': [expense.json() for expense in expenses]
               }, 200

    @jwt_required()
    def post(self):
        data = expense_parser.parse_args()
        current_user = get_jwt_identity()


        try:
            expense = ExpenseModel(data['date'], data['category'], data['amount'], current_user['user_id'])
            expense.save_to_db()
        except:
            return {
                       'message': 'An error occurred while saving expense data to the database',
                       'error': 'server_error'
                   }, 500

        return {
                   'expense': expense.json()
               }, 200
