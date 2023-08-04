from flask_wtf import FlaskForm
from wtforms import DateTimeField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class NoteForm(FlaskForm):
    """Форма заметки."""
    title = StringField(
        'Заголовок заметки',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 128)]
    )
    text = TextAreaField(
        'Напишите заметку', 
        validators=[DataRequired(message='Обязательное поле')]
    )
    deadline = StringField(validators=[Optional()])
    submit = SubmitField('Добавить')
