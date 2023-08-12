from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sgnotes_app import app, db, login_manager
from .models import Note, User
from .forms import NoteForm
from sqlalchemy import desc
from datetime import datetime


@app.route('/main-page', methods=['GET', 'POST'])
def main_page():
    return render_template('main.html')


@app.route('/', methods=['GET', 'POST'])
@login_required
def author_notes():
    """Главная страница пользователя. Содержит в себе поиск по методу POST.
    Сортирует по дате добавления.
    """
    user_id = current_user.id
    notes = Note.query.filter(Note.user_id==user_id).order_by(desc(Note.timestamp)).all()
    return render_template('author_notes.html', notes=notes)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        user_id = current_user.id
        if user_id:
            search_term = request.form['search_term']
            notes = Note.query.filter(Note.title.ilike(f'%{search_term}%')).filter(Note.user_id==user_id).order_by(desc(Note.timestamp)).all()
            return render_template('author_notes.html', notes=notes)
        else:
            flash('Поиск по заметкам доступен только для авторизованных пользователей!')
            return redirect(url_for('main_page'))


@app.route('/add-note', methods=['GET', 'POST'])
@login_required
def add_note():
    """Добавление заметки."""
    user_id = current_user.id
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            title=form.title.data, 
            text=form.text.data,
            user_id=user_id
        )
        if form.deadline.data:
            note.set_deadline(form.deadline.data)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('author_notes'))
    return render_template('add_notes.html', form=form)


@app.route('/delete/<int:note_id>', methods=['GET', 'POST'])
@login_required
def delete_note(note_id):
    """Удаление заметки."""
    user_id = current_user.id
    note = Note.query.get_or_404(note_id)
    if note.user_id == user_id:
        db.session.delete(note)
        db.session.commit()
        return redirect('/')
    else:
        return 'BANNED DEL!'


@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    """Редактирование заметки."""
    user_id = current_user.id
    note = Note.query.get_or_404(note_id)
    if note.user_id == user_id:
        if request.method == 'POST':
            note.title = request.form['title']
            note.text = request.form['text']
            if request.form['deadline']:
                note.set_deadline(request.form['deadline'])
            else:
                note.deadline = None
            db.session.commit()
            return redirect(url_for('author_notes'))
        return render_template('edit_notes.html', note=note)
    else:
        return 'BANNED UPD!!!!!!'


@app.route('/done/<int:note_id>', methods=['GET', 'POST'])
@login_required
def done_note(note_id):
    """Функция, которая отмечает задание выполненным."""
    user_id = current_user.id
    note = Note.query.get_or_404(note_id)
    if note.user_id == user_id:
        note.is_done = not note.is_done
        db.session.commit()
        return redirect(request.referrer)
    else:
        return 'BANNED DNNT!!!!!!!!!!'


@app.route('/done/', methods=['GET'])
@app.route('/undone/', methods=['GET'])
@login_required
def complete_task():
    """Страницы выполненных/невыполненных заданий."""
    user_id = current_user.id
    if request.path == '/done/':
        notes = Note.query.filter(Note.is_done==True).filter(Note.user_id==user_id).order_by(desc(Note.timestamp)).all()
    elif request.path == '/undone/':
        notes = Note.query.filter(Note.is_done==False).filter(Note.user_id==user_id).order_by(desc(Note.timestamp)).all()
    return render_template('author_notes.html', notes=notes)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('author_notes'))
        return 'Неверные данные входа'
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'user'
        user = User(username=username, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        user_id = current_user.id
        user = User.query.get(user_id)
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        if user and user.password == current_password:
            user.password = new_password
            db.session.commit()
            return 'Пароль успешно изменен'
        else:
            return 'Неверный текущий пароль'
    return render_template('change_password.html')


if __name__ == '__main__':
    app.run()
