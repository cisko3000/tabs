# Models (each of these classes has name of Table in fsender.db)
from flask.ext.sqlalchemy import SQLAlchemy
import datetime
db = SQLAlchemy()
class TimeEntry(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	start = db.Column(db.DateTime(), nullable=False)
	stop = db.Column(db.DateTime())
	delta = db.Column(db.Float())
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
	#project = db.relationship("Project", backref="time_entry")
	project = db.relationship("Project")
	billed = db.Column(db.Boolean())
	invoice_line_id = db.Column(db.Integer, db.ForeignKey('invoice_line.id'))
	invoice_line = db.relationship("InvoiceLine")

	def __init__(self):
		pass
	def __repr__(self):
		#return '<Project: %r \t start: %r \t stop: %r>' % (self.project_id,
		#									self.start.strftime("%x %X"),
		#									'self.stop.strftime("%x %X")'		  					  )
		return id
class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120))
	contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
	contact = db.relationship("Contact")
	notes = db.Column(db.Text())
	#time_entry_id = db.Column(db.Integer, db.ForeignKey('TimeEntry.id'))
	#time_entry_id = db.Column(db.Integer, db.ForeignKey('TimeEntry.id'))
	def __init__(self):
		pass
	def __repr__(self):
		return '%s: %s' % (self.contact, self.name)
	
class Contact(db.Model):
	def __init__(self, *args):
		if args and len(args) == 3:
			self.name = args[0]
			self.email = args[1]
			self.notes = args[2]
	id = db.Column(db.Integer, primary_key= True)
	name = db.Column(db.String(120))
	email = db.Column(db.String(120))
	notes = db.Column(db.Text())
	#project_id = db.Column(db.Integer, db.ForeignKey('Project.id'))
	#project = db.relationship("Project")
	def __repr__(self):
		return self.name + ' (' + self.email + ')'
	def __str__(self):
		return self.name

class Invoice(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	invoice_date = db.Column(db.DateTime(), nullable=False)
	contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
	contact = db.relationship("Contact")
	recipient_note = db.Column(db.String(240))
	subtotal = db.Column(db.Float())
	total = db.Column(db.Float())
	paid = db.Column(db.Boolean())
	def __repr__(self):
		return self.created+' '+self.amount+' '+self.paid
	def __str__(self):
		return self.created+' '+self.amount+' '+self.paid

class InvoiceLine(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(120))
	quantity = db.Column(db.Float())
	unit_price = db.Column(db.Float())
	amount = db.Column(db.Float())
	time_entries = db.relationship("TimeEntry") # Parent(this table) to Child(TimeEntry)
	def __repr__(self):
		return self.description
		return self.description