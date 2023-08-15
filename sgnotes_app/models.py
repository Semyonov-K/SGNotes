from datetime import datetime
from flask_login import UserMixin, current_user

from sgnotes_app import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    role = db.Column(db.String(10))
    notes = db.relationship('Note', backref='user', lazy=True)

    def __repr__(self):
        return '<Пользователь %r>' % (self.username)


class Note(db.Model):
    """Модель заметок."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=True)
    is_done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Заметка %r>' % (self.title)
    
    def get_formatted_timestamp(self):
        return self.timestamp.strftime('%d.%m.%Y')

    def set_deadline(self, deadline_str):
        self.deadline = datetime.fromisoformat(deadline_str)

    def get_formatted_deadline(self):
        if self.deadline:
            return self.deadline.strftime('%d.%m.%Y %H:%M')
        return None
    
    def get_notice(self):
        if self.deadline and self.is_done is False:
            if self.user_id == int(current_user.get_id()):
                current_time = datetime.now()
                print(current_time)
                time_difference = self.deadline - current_time
                print(time_difference)
                if time_difference.total_seconds() < 3600:
                    return self.title

    def to_dict(self):
        return dict(
            id = self.id,
            title = self.title,
            text = self.text,
            timestamp = self.timestamp,
            deadline = self.deadline,
            is_done = self.is_done
        )
    
    def from_dict(self, data):
        for field in ['title', 'text', 'source', 'added_by']:
            if field in data:
                setattr(self, field, data[field]) 
