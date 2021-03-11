from db import db
from datetime import datetime

class ExpenseModel(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80))
    amount = db.Column(db.Float(precision=2))
    date = db.Column(db.DateTime(timezone=False))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')

    def __init__(self, date, category, amount, user_id):
        self.date = datetime.strptime(date, '%Y-%m-%d')
        self.category = category
        self.amount = amount
        self.user_id = user_id

    def json(self):
        def calculate_quarter(month: int) -> int:
            if month < 4:
                return 1
            if month < 7:
                return 2
            if month < 10:
                return 3

            return 4

        return {
            'id': self.id,
            'date': {
                'date': self.date.strftime('%Y-%m-%d'),
                'dayOfWeek': self.date.weekday(),
                'dayOfMonth': self.date.day,
                'month': self.date.month,
                'year': self.date.year,
                'quarter': calculate_quarter(self.date.month)
            },
            'category': self.category,
            'amount': self.amount,
            'user': self.user.json()
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_all_by_category(cls, category):
        return cls.query.filter_by(category=category).all()

    @classmethod
    def get_all_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()
