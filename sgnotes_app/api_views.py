from flask import jsonify, request, g, session
from flask_login import login_user, logout_user, current_user
from functools import wraps
from http import HTTPStatus
import json
from datetime import datetime

from . import app, db
from .models import Note, User
from .error_handlers import InvalidAPIUsage


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return jsonify({'message': 'Неавторизованный доступ'}), HTTPStatus.UNAUTHORIZED
        g.user = User.query.get(session['user'])
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/notes/<int:id>/', methods=['GET'])
@login_required
def api_get_note(id):
    note = Note.query.filter_by(id=id, user=g.user).first()
    if note is None:
        raise InvalidAPIUsage(
            'Заметка не найдена',
            HTTPStatus.NOT_FOUND
        )
    return jsonify({'note': note.to_dict()}), HTTPStatus.OK


@app.route('/api/notes/<int:id>/', methods=['PATCH'])
@login_required
def api_update_note(id):
    data = request.get_json()
    note = Note.query.filter_by(id=id, user=g.user).first()
    if note is None:
        raise InvalidAPIUsage(
            'Заметка не найдена',
            HTTPStatus.NOT_FOUND
        )
    note.title = data.get('title', note.title)
    note.text = data.get('text', note.text)
    note.is_done = data.get('is_done', note.is_done)
    if 'deadline' in data:
        deadline = data['deadline']
        if deadline is None:
            note.deadline = None
        else:
            note.set_deadline(deadline)
    db.session.commit()  
    return jsonify({'note': note.to_dict()}), HTTPStatus.CREATED


@app.route('/api/notes/<int:id>/', methods=['DELETE'])
@login_required
def api_delete_note(id):
    note = Note.query.filter_by(id=id, user=g.user).first()
    if note is None:
        raise InvalidAPIUsage(
            'Заметка не найдена',
            HTTPStatus.NOT_FOUND
        )
    db.session.delete(note)
    db.session.commit()
    return '', HTTPStatus.NO_CONTENT


@app.route('/api/notes/', methods=['GET'])
@login_required
def api_get_notes():
    notes = Note.query.filter_by(user=g.user).all()  
    notes_list = [note.to_dict() for note in notes]
    return jsonify({'notes': notes_list}), HTTPStatus.OK


@app.route('/api/add_note/', methods=['POST'])
@login_required
def api_add_note():
    data = request.get_json()
    if 'title' not in data or 'text' not in data:
        raise InvalidAPIUsage('В запросе отсутствуют обязательные поля')
    note = Note()
    note.from_dict(data)
    if 'deadline' in data:
        note.set_deadline(data['deadline'])
    note.user_id = session['user']
    db.session.add(note)
    db.session.commit()
    return jsonify({'note': note.to_dict()}), HTTPStatus.CREATED


@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    users = User.query.filter(User.username==data['username']).first()
    if users:
        raise InvalidAPIUsage(
            'Такой пользователь уже существует!',
            HTTPStatus.BAD_REQUEST
        )
    if not data['username'] or not data['password']:
        return jsonify({'message': 'Некорректные данные'}), HTTPStatus.BAD_REQUEST
    user = User()
    user.from_dict(data)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Вы успешно зарегистрировались!'})


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        login_user(user)
        session['user'] = user.id
        return jsonify({'message': 'Вы успешно залогинились!'})
    raise InvalidAPIUsage(
                'Неправильный пароль или никнейм!',
                HTTPStatus.UNAUTHORIZED
    )


@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    session.pop('user', None)
    return jsonify({'message': 'Вы вышли из профиля'})


@app.route('/api/change_password', methods=['GET', 'POST'])
@login_required
def api_change_password():
    user_id = current_user.id
    user = User.query.get(user_id)
    if not user:
        raise InvalidAPIUsage(
                    'Пользователь не найден',
                    HTTPStatus.NOT_FOUND
        )
    data = request.get_json()
    if 'new_password' not in data:
        raise InvalidAPIUsage(
                    'Не указан новый пароль',
                    HTTPStatus.BAD_REQUEST
        )
    user.password = data['new_password']
    db.session.commit()
    return jsonify({'message': 'Пароль успешно изменен'})
