from datetime import datetime

from sgnotes_app import db


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     nickname = db.Column(db.String(64), unique = True)
#     email = db.Column(db.String(120), unique = True)
#     notes = db.relationship('Note', backref = 'author', lazy = 'dynamic')

#     def __repr__(self):
#         return '<Пользователь %r>' % (self.nickname)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=True)
    is_done = db.Column(db.Boolean, default=False)
    # user_nickname = db.Column(db.Integer, db.ForeignKey('user.nickname'))

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
