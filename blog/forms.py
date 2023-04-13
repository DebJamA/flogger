from flask_wtf import FlaskForm
from wtforms import validators, StringField, TextAreaField, FileField, SubmitField
#from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileAllowed

from blog.models import Category

def categories():
    return Category.query

class PostForm(FlaskForm):
    image = FileField('Image', validators=[
        FileAllowed(['jpg', 'png'], 'We only accept JPG or PNG images')
    ])   
    title = StringField('Title', [
            validators.InputRequired(),
            validators.Length(max=80)
        ])
    body = TextAreaField('Content', validators=[validators.InputRequired()])
    category = QuerySelectField('Category', query_factory=categories,
        allow_blank=True)
    new_category = StringField('New Category')

class CommentForm(FlaskForm):
    commenter = StringField('Your Name', validators=[validators.InputRequired()])
    body = StringField('Your Comment', validators=[validators.InputRequired()])
    submit = SubmitField('Comment')
