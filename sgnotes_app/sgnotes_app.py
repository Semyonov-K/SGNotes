from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sgnotes_app import app, db


@app.route('/')
def my_index_view():
    return render_template('registration.html')

if __name__ == '__main__':
    app.run()
