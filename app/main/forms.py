from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import Form, TextField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, URL

#forms section
class PostForm(FlaskForm):
    name = StringField('Username (Default Anonymous)')
    title = StringField('Title (Required)', validators=[DataRequired()])
    text = TextAreaField('Post Text (Optional)')
    link = StringField('Link to a Source (Optional)', validators=[URL()])
    file = MultipleFileField('Image/Audio Files Go Here (Optional)')
    submit = SubmitField('Submit')
