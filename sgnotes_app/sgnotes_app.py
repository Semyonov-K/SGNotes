from flask import Flask, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sgnotes_app import app, db
from models import Note

#check work github


@app.route('/')
def my_index_view():
    if 'username' in session:
        username = session['username']
        user_notes = Note.query.filter_by(user_nickname=username).all()
        return render_template('index.html', username=username, notes=user_notes)
    else:
        return redirect(url_for('register'))


@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == '__main__':
    app.run()
