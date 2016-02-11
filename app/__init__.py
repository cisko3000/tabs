# all the imports
from collections import namedtuple
from werkzeug.datastructures import MultiDict
from flask_bootstrap import Bootstrap, WebCDN
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from flask_admin import Admin
from flask_admin.base import MenuLink

from flask_admin.contrib.sqla import ModelView
# from flask.ext.sqlalchemy import SQLAlchemy
# Models
from models import *
from models import db
# Flask-WTF
from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form

# SQLAlchemy funcs
from sqlalchemy.sql import func

from wtforms import validators, widgets, TextField, SelectField, DecimalField, BooleanField, DateField, FieldList, FormField, FloatField, TextAreaField
from custom_wtforms import Select2Widget, Select2Field
# for data base init sqlite3 /tmp/flaskr.db < schema.sql
from contextlib import closing
from datetime import datetime, timedelta, time

from flask.ext.login import LoginManager, UserMixin
from flask.ext.login import login_required, login_user, current_user

from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField

# Import Form validators
from wtforms.validators import Required, Email, EqualTo, NoneOf, ValidationError


# create greg app
def create_app():
	app = Flask(__name__, static_url_path='')
	app.config.from_object('true_config')

	admin = Admin(app)
	db.init_app(app)
	with app.app_context():
		db.create_all()
	
	# Import modules 
	from app.mod_invoice.controllers import mod_invoice as invoice_module
	app.register_blueprint(invoice_module)
	
	Bootstrap(app)
	app.extensions['bootstrap']['cdns']["select2.js"] = WebCDN("//cdnjs.cloudflare.com/ajax/libs/select2/4.0.0/js/select2.min.js")
	app.extensions['bootstrap']['cdns']["select2.css"] = WebCDN("//cdnjs.cloudflare.com/ajax/libs/select2/4.0.0/css/select2.min.css")
	admin.add_view(ModelView(Contact,db.session))
	admin.add_view(ModelView(TimeEntry,db.session))
	admin.add_view(ModelView(Project,db.session))
	admin.add_view(ModelView(Invoice,db.session))
	admin.add_view(ModelView(InvoiceLine,db.session))
	admin.add_link(MenuLink('TBiller',endpoint='home'))

	login_manager = LoginManager()
	login_manager.init_app(app)
	login_manager.login_view = 'login'

	class User(UserMixin):
		def __init__(self, user_id):
			self.id = 1
		def get_name(self):
			return 'admin'

	@login_manager.user_loader
	def load_user(user_id):
		return User(1)

	class LoginForm(Form):
		username = TextField('Username',[Required()])
		pw = PasswordField('Password', [Required()])
	@app.route('/login',methods=['GET','POST'])
	def login():
		form = LoginForm(request.form)
		if form.validate_on_submit():
			if form.pw.data == app.config['PASSWORD'] and form.username.data == app.config['USERNAME']:
				user = User(1)
				login_user(user)
				next = request.args.get('next')
				flash('Logged in')
				return redirect(next or url_for('home'))
		return render_template('login.html', form=form)

	@app.before_request
	def check_for_maintenance():
		if app.config["MAINTENANCE"] == True:
			return 'Under Maintenance', 503
			#return redirect(url_for('maintenance'))

	@app.route('/new_appointment', methods=['GET','POST'])
	@login_required
	def new_contact():
		ContactForm = model_form(Contact, Form, field_args = {
				'notes' : {
				  'widget': widgets.TextArea()
				}
		})
		model = Contact()
		form = ContactForm(request.form, model)
		if request.method == 'POST':
			if form.validate():
					form.populate_obj(model)
					#model.created = datetime.now()
					db.session.add(model)
					db.session.commit()
					return 'success'
		return render_template('new_contact.html', form=form)
	
	@app.route('/', methods=['GET','POST'])
	@login_required
	def home():
		TimeEntryForm = model_form(TimeEntry, db_session=db.session, field_args = {
				'project' : {
					#'widget': Select2Widget(multiple = False),
					'widget': Select2Widget(),
					
				}
		})
		time_entry_model = TimeEntry()
		start_or_stop = 'Start'
		if request.method == 'POST':
			time_entry_form = TimeEntryForm(request.form, time_entry_model)
			time_entry_form.populate_obj(time_entry_model)
			if TimeEntry.query.filter_by(stop=None).first() == None:
				time_entry_model.start = datetime.now().replace(second=0, microsecond=0)
				time_entry_model.project_id = int(request.form['project'])
				time_entry_model.project = Project.query.filter_by(id=int(request.form['project'])).first()
				db.session.add(time_entry_model)
				db.session.commit()
			else:
				time_entry_model = TimeEntry.query.filter_by(stop=None).first()
				#TimeEntry.query.filter_by(project=time_entry_model.project).filter_by(stop=None).first().stop \
				#= datetime.now().replace(second=0, microsecond=0)
				time_entry_model.stop = datetime.now().replace(second = 0 , microsecond = 0)
				temp_delta = time_entry_model.stop - time_entry_model.start
				#temp_delta = temp_delta / timedelta(seconds=60)
				time_entry_model.delta = round(float(float(temp_delta.seconds/60)/60),2)
				db.session.flush()
				db.session.commit()
		time_entry_form = TimeEntryForm(request.form, time_entry_model)
		#raise ValueError('test')
		if TimeEntry.query.filter_by(stop=None).first() != None:
			TimeEntryForm.project = TextField()
			time_entry_form = TimeEntryForm(request.form, time_entry_model)
			time_entry_form.project.data = TimeEntry.query.filter_by(stop=None).first().project
			start_or_stop = 'Stop'
		monday = datetime.today()
		while monday.weekday() != 0:
			monday += timedelta(days=-1)
		monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
		sunday = monday + timedelta(days = 6)
		#raise ValueError(monday.strftime('%x %I:%m %p')+' '+sunday.strftime('%x %I:%m %p'))
		entries = TimeEntry.query.filter(TimeEntry.start >= monday).filter(TimeEntry.start < sunday + timedelta(days=1) ).all()
		
		week_total = db.session.query(
							#func.max(Score.score).label("max_score"), 
		                    func.sum(TimeEntry.delta).label("Total")
		                    ).filter(TimeEntry.start >= monday).filter(TimeEntry.start < sunday + timedelta(days=1) ).filter(TimeEntry.delta != None).first()
		if week_total.Total == None:
			week_total = "%0.2f" % (0)
		else:
			week_total = "%0.2f" % (week_total.Total)
		total_today = db.session.query(func.sum(TimeEntry.delta).label("Total"))
		total_today = total_today.filter(TimeEntry.start >= datetime.combine(datetime.today(), time.min))
		total_today = total_today.filter(TimeEntry.start <= datetime.combine(datetime.today(), time.max))
		total_today = total_today.filter(TimeEntry.delta != None).first()
		if total_today.Total == None:
			total_today = "%0.2f" % (0)
		else:
			total_today = "%0.2f" % (total_today.Total)

		#qry = qry.group_by(Score.some_group_column)
		#for _res in qry.all():
		#    print _res


		#total = db.session.query(TimeEntry)
		return render_template('home.html', time_entry_form=time_entry_form, entries = entries,
			start_or_stop = start_or_stop, monday = monday, sunday= sunday, week_total = week_total, total_today = total_today)
	@app.route('/totals')
	@login_required
	def totals():
		projects = Project.query.all()
		the_data = []
		for project in projects:
			entries = TimeEntry.query.filter_by(project_id = project.id).all()
			the_sum = 0
			for entry in entries:
				the_sum += entry.delta
			the_data.append((project.name, '% 3.2f'%the_sum))
		return render_template('totals.html', the_data = the_data)
	@app.route('/robots.txt')
	def robots():
		return '''User-agent: *
	Disallow: /'''

	@app.route('/admin')
	@login_required
	def admin():
		return redirect('/admin')
	return app

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0',port=3000)
	