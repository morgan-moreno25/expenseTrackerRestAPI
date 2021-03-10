from db import db


class ExpenseModel(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80))
    amount = db.Column(db.Float(precision=2))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')

    def __init__(self, category, amount, user_id):
        self.category = category
        self.amount = amount
        self.user_id = user_id

    def json(self):
        return {
            'id': self.id,
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
