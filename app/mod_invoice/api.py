from flask import Flask, Blueprint, jsonify, request
from flask_restful import Resource, Api, reqparse, abort
from flask_restful import fields, marshal_with
from flask.ext.login import login_required
from app.models import Contact, Project, TimeEntry, Invoice, InvoiceLine
from datetime import datetime
from sqlalchemy.sql import func, or_

from .. import db

# Marshals
invoice_fields = {
	'id' : fields.Integer,
	'invoice_date' : fields.Date,
	'contact_id' : fields.Integer,
	'contact' : fields.String,
	'recipient_note' : fields.String,
	'subtotal' : fields.Decimal,
	'total' : fields.Decimal,
	'paid' : fields.Decimal,	
}
invoice_line_fields = {
	'id': fields.Integer,
	'description' : fields.String,
	'quantity': fields.Decimal,
	'unit_price' : fields.Decimal,
	'amount' : fields.Decimal,
	'invoice_id' : fields.Integer,
}

def abort_if_dne(model_type, model_id):
	if not db.session.query(model_type).get(model_id):
		abort(404, message="%s %s doesn't exist" % (model_type, model_id))

parser = reqparse.RequestParser(bundle_errors = True)
parser.add_argument('invoice_id', type=int, help="Invoice ID")
parser.add_argument('sstr', type=str, help="Search String", location="args")

# For invoice creation
parser.add_argument('contact_id',     type=int, help="Contact ID")
parser.add_argument('email', 	      type=str, help="Email")
parser.add_argument('invoice_date',   type=str, help="Invoice Date")
parser.add_argument('recipient_note', type=str, help="Recipient Note")
parser.add_argument('subtotal', 	  type=str, help="Subtotal")
parser.add_argument('total', 		  type=str, help="Total")
# TODO investigate how to add a list as argument


# Single Resources
class TabsInvoice(Resource):
	decorators =[login_required]
	@marshal_with(invoice_fields)
	def get(self, invoice_id):
		abort_if_dne(Invoice, invoice_id)
		return Invoice.query.get(invoice_id)
	@marshal_with(invoice_fields)
	def delete(self, invoice_id):
		abort_if_dne(Invoice, invoice_id)
		to_del = Invoice.query.get(invoice_id)
		db.session.delete(to_del)
		db.session.commit()
		return []
	def put(self, invoice_id):
		abort_if_dne(Invoice, invoice_id)
		args = parser.parse_args()
		inv = Invoice.query.get(invoice_id)
		#inv.name = args['contact_name']
		#inv.email = args['contact_email']
		#inv.notes = args['contact_notes']
		db.session.commit()
		return c
class InvoiceList(Resource):
	decorators = [login_required]
	@marshal_with(invoice_fields)
	def get(self):
		try:
			args = parser.parse_args()
			search_string = args['sstr']
			if search_string == '':
				return Invoice.query.all()
			else:
				return Invoice.query.join(Contact).join(Project).filter(
					or_(
						Contact.name.contains(search_string),
						Project.name.contains(search_string),
						)
					).all()
		except:
			pass
		return Invoice.query.all()
	def post(self):
		args = parse.parse_args()
		try:
			c_id = args['contact_id']
			dcontact = Contact.query.get(c_id).first()
		except:
			abort(404, message="Contact id: %s doesn't exist" % (c_id))
		inv = Invoice()
		inv.email = args['email']
		inv.invoice_date = args['invoice_date']
		inv.recipient_note = args['recipient_note']
		inv.subtotal = args['subtotal']
		inv.total = args['total']
		inv.paid = False
		inv.contact_id = c_id
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
		# inv_lines (from list in args)
		the_items = []
		for the_item in inv_lines:
			# append to the_items (for paypal)
			the_items.append(dict({"name":the_item.d_description.data,"quantity":str(the_item.qty.data),"unit_price":{"currency":"USD","value":str(the_item.unit_price.data)}}))
			# Create and append to Invoice model
			new_invoice_line = InvoiceLine()
			new_invoice_line.description
			new_invoice_line.quantity
			new_invoice_line.unit_price
			new_invoice_line.amount
			inv.invoice_lines.append(new_invoice_line)	
		paypal_invoice.items = the_items
		error = None
		if paypal_invoice.create():
			print('paypal invoice created')
			# Add invoice lines here (from list as argument) 
			db.session.add(inv)
			db.session.commit()
		else:
			error = paypal_invoice.error
			abort(404, message="Invoice creation error: %s" % (error)) 
		return inv, 201
