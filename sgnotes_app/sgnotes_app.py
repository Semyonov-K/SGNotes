from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sgnotes_app import app, db


@app.route('/')
def my_index_view():
    return 'Это мой первый Flask-проект'

if __name__ == '__main__':
    app.run()
