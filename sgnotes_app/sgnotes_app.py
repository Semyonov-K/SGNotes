from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sgnotes_app import app, db
from .models import Note
from .forms import NoteForm
from sqlalchemy import desc
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
def author_notes():
    if request.method == 'POST':
        search_term = request.form['search_term']
        notes = Note.query.filter(Note.title.ilike(f'%{search_term}%')).order_by(desc(Note.timestamp)).all()
    else:
        notes = Note.query.order_by(desc(Note.timestamp)).all()
    return render_template('author_notes.html', notes=notes)
    # if 'username' in session:
    #     username = session['username']
    #     user_notes = Note.query.filter_by(user_nickname=username).all()
    #     return render_template('index.html', username=username, notes=user_notes)
    # else:
    #     return redirect(url_for('register'))


@app.route('/add-note', methods=['GET', 'POST'])
def add_note():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            title=form.title.data, 
            text=form.text.data, 
        )
        if form.deadline.data:
            note.set_deadline(form.deadline.data)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('author_notes'))
    return render_template('add_notes.html', form=form)


@app.route('/delete/<int:note_id>', methods=['GET', 'POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return redirect('/')


@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
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


@app.route('/done/<int:note_id>', methods=['GET', 'POST'])
def done_note(note_id):
    note = Note.query.get_or_404(note_id)
    note.is_done = not note.is_done
    db.session.commit()
    return redirect(request.referrer)


@app.route('/done/', methods=['GET'])
@app.route('/undone/', methods=['GET'])
def complete_task():
    if request.path == '/done/':
        notes = Note.query.filter(Note.is_done==True).order_by(desc(Note.timestamp)).all()
    elif request.path == '/undone/':
        notes = Note.query.filter(Note.is_done==False).order_by(desc(Note.timestamp)).all()
    return render_template('author_notes.html', notes=notes)


@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == '__main__':
    app.run()
