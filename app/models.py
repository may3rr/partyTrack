from flask_login import UserMixin
from app import login, mongo
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')

    @staticmethod
    def get_by_id(user_id):
        try:
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            return User(user_data) if user_data else None
        except:
            return None

@login.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(16))
    id_card_number = db.Column(db.String(18), unique=True)
    member_type = db.Column(db.String(32), nullable=False, default='学生党员')  # '学生党员' or '教师党员'
    status = db.Column(db.String(32), nullable=False, default='积极分子') # '积极分子', '发展对象', '预备党员', '正式党员', '已归档'
    mentors = db.Column(db.String(128))

    # Development dates
    application_date = db.Column(db.Date, nullable=True)
    activist_date = db.Column(db.Date, nullable=True)
    development_object_date = db.Column(db.Date, nullable=True)
    pre_member_date = db.Column(db.Date, nullable=True)
    full_member_date = db.Column(db.Date, nullable=True)

    submissions = db.relationship('Submission', backref='member', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Member {self.name}>'

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    submission_date = db.Column(db.Date, nullable=False)
    submission_type = db.Column(db.String(64), default='思想汇报')

    def __repr__(self):
        return f'<Submission {self.id} for Member {self.member_id}>'

class DismissedReminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reminder_id = db.Column(db.String(128), unique=True, nullable=False)
    dismissed_at = db.Column(db.DateTime, default=datetime.utcnow) 