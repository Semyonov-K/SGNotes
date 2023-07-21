from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class NoteForm(FlaskForm):
    title = StringField(
        'Заголовок заметки',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 128)]
    )
    text = TextAreaField(
        'Напишите заметку', 
        validators=[DataRequired(message='Обязательное поле')]
    )
    deadline = DateField(validators=[Optional()])
    submit = SubmitField('Добавить')
