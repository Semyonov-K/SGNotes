from flask import jsonify, request
from http import HTTPStatus

from . import app, db
from .models import Note
from .error_handlers import InvalidAPIUsage


@app.route('/api/notes/<int:id>/', methods=['GET'])  
def get_note(id):
    note = Note.query.get(id)
    if note is None:
        raise InvalidAPIUsage('Мнение с указанным id не найдено', HTTPStatus.NOT_FOUND)
    return jsonify({'note': note.to_dict()}), HTTPStatus.OK


@app.route('/api/notes/<int:id>/', methods=['PATCH'])
def update_note(id):
    data = request.get_json()
    if (
        'text' in data and 
        Note.query.filter_by(text=data['text']).first() is not None
    ):
        raise InvalidAPIUsage('Такое мнение уже есть в базе данных')
    note = Note.query.get(id)
    if note is None:
        raise InvalidAPIUsage('Мнение с указанным id не найдено', HTTPStatus.NOT_FOUND)
    note.title = data.get('title', note.title)
    note.text = data.get('text', note.text)
    note.source = data.get('source', note.source)
    note.added_by = data.get('added_by', note.added_by)
    db.session.commit()  
    return jsonify({'note': note.to_dict()}), HTTPStatus.CREATED


@app.route('/api/notes/<int:id>/', methods=['DELETE'])
def delete_note(id):
    note = Note.query.get(id)
    if note is None:
        raise InvalidAPIUsage('Мнение с указанным id не найдено', HTTPStatus.NOT_FOUND)
    db.session.delete(note)
    db.session.commit()
    return '', HTTPStatus.NO_CONTENT


@app.route('/api/notes/', methods=['GET'])
def get_notes():
    notes = Note.query.all()  
    notes_list = [note.to_dict() for note in notes]
    return jsonify({'notes': notes_list}), HTTPStatus.OK


@app.route('/api/notes/', methods=['POST'])
def add_note():
    data = request.get_json()
    if 'title' not in data or 'text' not in data:
        raise InvalidAPIUsage('В запросе отсутствуют обязательные поля')
    note = Note()
    note.from_dict(data)
    db.session.add(note)
    db.session.commit()
    return jsonify({'note': note.to_dict()}), HTTPStatus.CREATED
