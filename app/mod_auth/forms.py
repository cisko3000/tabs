from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, BooleanField, SubmitField, PasswordField

from wtforms.validators import Required, Email, EqualTo, ValidationError, Optional
from app.mod_auth.models import User
from flask.ext.sqlalchemy import SQLAlchemy
from .. import db

class LoginForm(Form):
	email = TextField('Email Address',
		[Email(), Required(message='Forgot your email address?')])
	password = PasswordField('Password',
		[Required(message='Must provide a password.')])
	remember = BooleanField('Remember me')
	submit = SubmitField('Sign in')
	