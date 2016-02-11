from flask import Blueprint, request, render_template, redirect, url_for
from flask.ext.login import login_required, current_user

from flask.ext.wtf import Form
from wtforms import validators, widgets, TextField, SelectField, DecimalField, BooleanField, DateField, FieldList, FormField, FloatField, TextAreaField
from .. import db
from app.models import *


mod_invoice = Blueprint('tabs_invoice', __name__, url_prefix='/invoice')


@mod_invoice.route('/create_invoice', methods=['POST'])
@login_required
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
@mod_invoice.route('/create_invoice_final', methods = ['POST'])
@login_required
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
			"client_id": app.config['PAYPAL_CLIENT_ID'], # PAYPAL_CLIENT_ID
			"client_secret": app.config['PAYPAL_CLIENT_SECRET'] })		# PAYPAL_CLIENT_SECRET
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
			"note":"MAKE MONEY F*CK B*TCHES"
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
@mod_invoice.route('/invoices',methods=['GET'])
@login_required
def invoices():
	try: error
	except NameError: error = None 
	class CreateInvoiceForm(Form):
		contact = SelectField()
	create_invoice_form = CreateInvoiceForm()
	create_invoice_form.contact.choices = [(str(contact.name),str(contact.name)) for contact in Contact.query.all()]
	invoices = Invoice.query.all()
	return render_template('invoices.html',invoices=invoices, create_invoice_form=create_invoice_form, error=error)

