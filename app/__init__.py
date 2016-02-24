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
from app.models import *
from app.mod_auth.models import *
from app.mod_auth.forms import *
from app.models import db
# Flask-WTF
from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
#from sqlalchemy import or_

# SQLAlchemy funcs
from sqlalchemy.sql import func, or_

from wtforms import validators, widgets, TextField, SelectField, DecimalField, BooleanField, DateField, FieldList, FormField, FloatField, TextAreaField
from custom_wtforms import Select2Widget, Select2Field
# for data base init sqlite3 /tmp/flaskr.db < schema.sql
from contextlib import closing
from datetime import datetime, timedelta, time

from flask.ext.login import LoginManager, UserMixin
from flask.ext.login import login_required, login_user, logout_user, current_user

from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField

# Import Form validators
from wtforms.validators import Required, Email, EqualTo, NoneOf, ValidationError
from mod_auth.forms import LoginForm

# Import password / encryption helper tools
from werkzeug import check_password_hash, \
	generate_password_hash


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
	from app.mod_api.api import api_mod as api_module
	app.register_blueprint(invoice_module)
	app.register_blueprint(api_module)
	
	Bootstrap(app)
	app.extensions['bootstrap']['cdns']["select2.js"] = WebCDN("//cdnjs.cloudflare.com/ajax/libs/select2/4.0.0/js/select2.min.js")
	app.extensions['bootstrap']['cdns']["select2.css"] = WebCDN("//cdnjs.cloudflare.com/ajax/libs/select2/4.0.0/css/select2.min.css")
	app.extensions['bootstrap']['cdns']['cosmo'] = WebCDN("https://cdnjs.cloudflare.com/ajax/libs/bootswatch/3.3.5/cosmo/")
	app.extensions['bootstrap']['cdns']['simplex'] = WebCDN("https://cdnjs.cloudflare.com/ajax/libs/bootswatch/3.3.5/simplex/")
	app.extensions['bootstrap']['cdns']['cyborg'] = WebCDN("https://cdnjs.cloudflare.com/ajax/libs/bootswatch/3.3.5/cyborg/")
	app.extensions['bootstrap']['cdns']['paper'] = WebCDN("https://cdnjs.cloudflare.com/ajax/libs/bootswatch/3.3.5/paper/")
	app.extensions['bootstrap']['cdns']['sandstone'] = WebCDN("https://cdnjs.cloudflare.com/ajax/libs/bootswatch/3.3.5/sandstone/")

	admin.add_view(ModelView(Contact,db.session))
	admin.add_view(ModelView(TimeEntry,db.session))
	admin.add_view(ModelView(Project,db.session))
	admin.add_view(ModelView(Invoice,db.session))
	admin.add_view(ModelView(InvoiceLine,db.session))
	admin.add_view(ModelView(User,db.session))
	admin.add_link(MenuLink('TBiller',endpoint='home'))

	login_manager = LoginManager()
	login_manager.init_app(app)
	login_manager.login_view = 'login'

	
	class TabsUser(UserMixin):
		def __init__(self, user_id):
			self.id = 1
		def get_name(self):
			return user.name
	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(user_id)

	@app.route('/login',methods=['GET','POST'])
	def login():
		form = LoginForm(request.form)
		if form.validate_on_submit():
			user = User.query.filter(User.email == form.email.data).first()
			if user and check_password_hash(user.password, form.password.data) and user.status == 0:
				print(user)
				print('User exists')
				login_user(user)
				next = request.args.get('next')
				flash('Logged in')
				return redirect(next or url_for('home'))
		return render_template('auth/login.html', form=form)
	@app.route('/register', methods=['GET','POST'])
	def register():
		form = RegisterForm(request.form)
		if form.validate_on_submit():
			user = User.query.filter(
					or_(User.email==form.email.data,
						User.username==form.username.data)
				).first()
			if user:
				flash('Username or email taken.')
				return render_template("register.html", form = form)
			new_user = User('','','')
			form.populate_obj(new_user)
			new_user.username = form.username.data
			new_user.status = 0
			new_user.password = generate_password_hash(new_user.password)
			db.session.add(new_user)
			db.session.commit()
			flash('Success: User Registered')
			return redirect(url_for('home'))
		return render_template("auth/register.html", form = form)



	@app.route('/logout', methods=['GET'])
	def logout():
		logout_user()
		return redirect('/login')

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
	@app.route('/tabs_admin', methods=['GET'])
	@login_required
	def tabs_admin():
		return render_template('tabs_admin.html')
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
		#raise ValueError(entries)

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
	
