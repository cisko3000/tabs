from flask.ext.sqlalchemy import SQLAlchemy
from .. import db
class Base(db.Model):
	__abstract__ = True
	id = db.Column(db.Integer, primary_key = True)
	date_create = db.Column(db.DateTime, default = db.func.current_timestamp())
	date_modified = db.Column(
		db.DateTime,
		default = db.func.current_timestamp(),
		onupdate = db.func.current_timestamp()
		)
class User(Base):
	__tablename__ = 'auth_user'
	username = db.Column(db.String(64), nullable = False, unique = True)
	email = db.Column(db.String(128), nullable = False, unique = True)
	password = db.Column(db.String(192), nullable = False)
	status = db.Column(db.SmallInteger, nullable=False)
	# New instance instantiation procedure
	def __init__(self, name, email, password):
		self.email = email
		self.password = password
		self.status = 0
	def __repr__(self):
		return '<User %r>' % (self.email)
	def is_authenticated(self):
		return True
	def is_active():
		if self.status == 1:
			return True
		return False
	def is_anonymous(self):
		return False
	def get_id(user):
		return str(user.id)