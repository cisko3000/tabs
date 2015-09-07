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
from wtforms import validators, widgets, TextField, SelectField, DecimalField, BooleanField, DateField, FieldList, FormField, FloatField, TextAreaField
from custom_wtforms import Select2Widget, Select2Field
# for data base init sqlite3 /tmp/flaskr.db < schema.sql
from contextlib import closing
from datetime import datetime, timedelta

# create greg app
app = Flask(__name__, static_url_path='')
app.config.from_object('config')
admin = Admin(app)
db.init_app(app)
Bootstrap(app)
app.extensions['bootstrap']['cdns']["select2.js"] = WebCDN("//cdnjs.cloudflare.com/ajax/libs/select2/4.0.0/js/select2.min.js")
app.extensions['bootstrap']['cdns']["select2.css"] = WebCDN("//cdnjs.cloudflare.com/ajax/libs/select2/4.0.0/css/select2.min.css")
admin.add_view(ModelView(Contact,db.session))
admin.add_view(ModelView(TimeEntry,db.session))
admin.add_view(ModelView(Project,db.session))
admin.add_view(ModelView(Invoice,db.session))
admin.add_view(ModelView(InvoiceLine,db.session))
admin.add_link(MenuLink('TBiller',endpoint='home'))

@app.before_request
def check_for_maintenance():
	if app.config["MAINTENANCE"] == True:
		return 'Under Maintenance', 503
		#return redirect(url_for('maintenance'))

@app.route('/new_appointment', methods=['GET','POST'])
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
@app.route('/create_invoice', methods=['POST'])
def create_invoice():
	contact = request.form['contact']
	contact = db.session.query(Contact).filter(Contact.name==contact).first()
	class InvoiceLineForm(Form):
		d_description = TextField()
		qty = DecimalField()
		unit_price = DecimalField()
	class InvoiceForm(Form):
		email = TextField()
		created = DateField(format='%m/%d/%Y')
		amount = DecimalField()
		paid = BooleanField()
		# min_entries = 1 
		invoice_line = FieldList(FormField(InvoiceLineForm))
	invoice_form = InvoiceForm()
	invoice_form.created.data = datetime.today()
	the_projects = db.session.query(Project).filter(Project.contact==contact)
	invoice_form.email.data = the_projects.first().contact.email
	#the_entries = db.session.query(TimeEntry).filter(TimeEntry.billed!=True)
	the_entries = db.session.query(TimeEntry).filter(TimeEntry.billed.is_(None))
	invoice_lines_list = []
	the_rate = float(25)
	for a_project in the_projects:
		invoice_line = InvoiceLineForm()
		invoice_line.d_description.data = a_project.name
		invoice_line.unit_price.data = the_rate
		invoice_line.qty.data = sum([float(x.delta) for x in the_entries.filter_by(project=a_project)])
		invoice_lines_list.append(invoice_line.qty.data)
		if invoice_line.qty.data != 0:
			invoice_form.invoice_line.append_entry(invoice_line.data)
	invoice_form.amount.data = sum([ float(x)*the_rate for x in invoice_lines_list])
	length = len([x for x in the_projects])
	return render_template('invoice_view.html',invoice_form=invoice_form, length = length)
@app.route('/create_invoice_final', methods = ['POST'])
def create_invoice_final():
	class InvoiceLineForm(Form):
		d_description = TextField()
		qty = DecimalField()
		unit_price = DecimalField()
	class InvoiceForm(Form):
		email = TextField()
		invoice_date = DateField(format='%m/%d/%Y')
		contact_id = TextField()
		recipient_note = TextField()
		subtotal = DecimalField()
		total = DecimalField()
		paid = BooleanField()
		invoice_line = FieldList(FormField(InvoiceLineForm))
	import paypalrestsdk
	paypalrestsdk.configure({
			"mode": "sandbox", # PAYPAL_MODE
			"client_id": "client_ID972397427442", # PAYPAL_CLIENT_ID
			"client_secret": "client_SECRET03928049494" })		# PAYPAL_CLIENT_SECRET
	paypal_invoice = paypalrestsdk.Invoice({
			"merchant_info": {
				"email":"fake@email.com",
				"first_name":"Francisco",
				"last_name": "Barcena",
				"business_name":"fdev.tk",
				"phone":{"country_code": "001","national_number":"5555555555"},
				"address":{
					"line1":"123 Fake St. Apt.A",
					"city":"Fake City",
					"country_code":"US",
					"state":"California"
				},
			},
			"billing_info":[{"email":request.form["email"]}],
			"note":"MAKE MONEY FUCK BITCHES"
	})
	invoice_form = InvoiceForm(request.form)
	the_items = []
	for the_item in invoice_form.invoice_line:
		the_items.append(dict({"name":the_item.d_description.data,"quantity":str(the_item.qty.data),"unit_price":{"currency":"USD","value":str(the_item.unit_price.data)}}))
	paypal_invoice.items = the_items
	error = None
	if paypal_invoice.create():
		#return ("Invoice[%s] created successfully" % (invoice.id,))
		flash('Invoice successfully created')
		invoice_model = Invoice()
		invoice_form.populate_obj(invoice_model)
		invoice_model.invoice_date = datetime.now().replace(second = 0 , microsecond = 0)
		invoice_model.contact_id = db.session.query(Contact).filter_by(Contact.email == request.form["email"]).first().id
		invoice_model.recipient_note ='Test'
		db.session.add(invoice_model)
		db.session.commit()
		# return redirect('/invoices')
		return redirect('/invoices')
	else:
		errror = paypal_invoice.error
		return redirect('/invoices')
		#return 'failure'
@app.route('/invoices',methods=['GET'])
def invoices():
	try: error
	except NameError: error = None 
	class CreateInvoiceForm(Form):
		contact = SelectField()
	create_invoice_form = CreateInvoiceForm()
	create_invoice_form.contact.choices = [(str(contact.name),str(contact.name)) for contact in Contact.query.all()]
	invoices = Invoice.query.all()
	return render_template('invoices.html',invoices=invoices, create_invoice_form=create_invoice_form, error=error)


@app.route('/', methods=['GET','POST'])
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
	entries = TimeEntry.query.all()
	return render_template('home.html', time_entry_form=time_entry_form, entries = entries, start_or_stop = start_or_stop)

@app.route('/robots.txt')
def robots():
	return '''User-agent: *
Disallow: /'''
@app.route('/admin')
def admin():
	return redirect('/admin')
if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0',port=3000)
	
