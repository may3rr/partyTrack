from app import mongo, login_manager
from werkzeug.security import check_password_hash
from flask_login import UserMixin
from datetime import datetime
from bson import ObjectId

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data
        
    def get_id(self):
        return str(self.user_data.get('_id'))
        
    @property
    def is_authenticated(self):
        return True
        
    @property
    def is_active(self):
        return True
        
    @property
    def is_anonymous(self):
        return False
        
    def check_password(self, password):
        return check_password_hash(self.user_data.get('password_hash'), password)

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if not user_data:
        return None
    return User(user_data)

def create_member(data):
    return mongo.db.members.insert_one(data)

def get_member(member_id):
    return mongo.db.members.find_one({'_id': ObjectId(member_id)})

def update_member(member_id, data):
    return mongo.db.members.update_one(
        {'_id': ObjectId(member_id)},
        {'$set': data}
    )

def delete_member(member_id):
    return mongo.db.members.delete_one({'_id': ObjectId(member_id)})

def create_submission(data):
    return mongo.db.submissions.insert_one(data)

def get_submissions_for_member(member_id):
    return mongo.db.submissions.find({'member_id': str(member_id)})

def dismiss_reminder(reminder_id):
    return mongo.db.dismissed_reminders.insert_one({
        'reminder_id': reminder_id,
        'dismissed_at': datetime.utcnow()
    }) 