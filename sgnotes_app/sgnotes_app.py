from flask import Flask, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sgnotes_app import app, db
from .models import Note
from .forms import NoteForm
from sqlalchemy import desc


@app.route('/')
def author_notes():
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
        deadline = form.deadline.data
        note = Note(
            title=form.title.data, 
            text=form.text.data, 
            deadline=deadline
        )
        if form.deadline.data is not None:
            note.set_deadline(deadline)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('author_notes'))
    return render_template('add_notes.html', form=form)


@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == '__main__':
    app.run()
