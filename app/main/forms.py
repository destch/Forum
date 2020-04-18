from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, MultipleFileField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, Regexp, URL
from wtforms import ValidationError
from ..models import Role, User





# forms section
class ThreadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(0, 256)])
    body = TextAreaField('Body', render_kw={'class': 'form-control', 'rows': 5})
    scene = SelectField(u'Post to Scene (Optional)', choices=[('',''),('Los Angeles', 'Los Angeles'), ('NYC', 'NYC'),
                                                              ('Chicago', 'Chicago')])
    type = 'thread'
    image = FileField('Post Thumbnail (Optional)')
    submit = SubmitField('Submit')


# forms section
class LinkForm(FlaskForm):
    link = StringField('Link', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired(), Length(0, 256)])
    body = TextAreaField('Body (Optional)', render_kw={'class': 'form-control', 'rows': 5})
    scene = SelectField(u'Post to Scene (Optional)', choices=[('',''),('Los Angeles', 'Los Angeles'), ('NYC', 'NYC'),
                                                              ('Chicago', 'Chicago')])
    type = 'link'
    image = FileField('Post Thumbnail (Optional)')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    body = TextAreaField('Body', render_kw={'class': 'form-control', 'rows': 5})
    submit = SubmitField('Submit')