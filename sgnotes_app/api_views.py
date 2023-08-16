from flask import jsonify, request
from flask_login import login_user, login_required, logout_user, current_user
from functools import wraps
from http import HTTPStatus
import json

from . import app, db
from .models import Note, User
from .error_handlers import InvalidAPIUsage


def check_authentication(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        else:
            response = {
                'error': 'Вы не авторизованы'
            }
            return json.dumps(response), HTTPStatus.UNAUTHORIZED, {'Content-Type': 'application/json'}
    return wrapper


@app.route('/api/notes/<int:id>/', methods=['GET'])
@login_required
@check_authentication
def api_get_note(id):
    if current_user.is_authenticated:
        note = Note.query.get(id)
        if note is None:
            raise InvalidAPIUsage(
                'Заметка не найдена',
                HTTPStatus.NOT_FOUND
            )
        return jsonify({'note': note.to_dict()}), HTTPStatus.OK
    else:
        return jsonify({'message': 'Не авторизован'}), HTTPStatus.UNAUTHORIZED


@app.route('/api/notes/<int:id>/', methods=['PATCH'])
@login_required
@check_authentication
def api_update_note(id):
    data = request.get_json()
    note = Note.query.get(id)
    if note is None:
        raise InvalidAPIUsage(
            'Заметка не найдена',
            HTTPStatus.NOT_FOUND
        )
    note.title = data.get('title', note.title)
    note.text = data.get('text', note.text)
    note.source = data.get('source', note.source)
    note.added_by = data.get('added_by', note.added_by)
    db.session.commit()  
    return jsonify({'note': note.to_dict()}), HTTPStatus.CREATED


@app.route('/api/notes/<int:id>/', methods=['DELETE'])
@login_required
@check_authentication
def api_delete_note(id):
    note = Note.query.get(id)
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
@check_authentication
def api_get_notes():
    notes = Note.query.all()  
    notes_list = [note.to_dict() for note in notes]
    return jsonify({'notes': notes_list}), HTTPStatus.OK


@app.route('/api/add_note/', methods=['POST'])
@login_required
@check_authentication
def api_add_note():
    data = request.get_json()
    if 'title' not in data or 'text' not in data:
        raise InvalidAPIUsage('В запросе отсутствуют обязательные поля')
    note = Note()
    note.from_dict(data)
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
        return jsonify({'message': 'Вы успешно залогинились!'})
    raise InvalidAPIUsage(
                'Неправильный пароль или никнейм!',
                HTTPStatus.UNAUTHORIZED
    )


@app.route('/api/logout', methods=['POST'])
@login_required
@check_authentication
def api_logout():
    logout_user()
    return jsonify({'message': 'Вы вышли из профиля'})


@app.route('/api/change_password', methods=['GET', 'POST'])
@login_required
@check_authentication
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
