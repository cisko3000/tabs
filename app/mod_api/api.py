from flask import Flask, Blueprint, jsonify
from flask_restful import Resource, Api, reqparse, abort
from flask_restful import fields, marshal_with
from flask.ext.login import login_required
from app.models import Contact, Project
from .. import db

api_mod = Blueprint('api', __name__, url_prefix = '/api')
api = Api(api_mod)

resource_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'email': fields.String,
	'notes': fields.String,
	#'Contact': fields.List,
	# takes an endpoint name and generates a URL for that endpoint in the response
	# useful for paging
	'uri': fields.Url('new_contact')
}
def abort_if_dne(model_type, model_id):
	if not db.session.query(model_type).get(model_id):
		abort(404, message="%s %s doesn't exist" % (model_type, model_id))


parser = reqparse.RequestParser()
parser.add_argument('contact_name',  type=str, help='Contact Name')
parser.add_argument('contact_email', type=str, help='Contact Email')
parser.add_argument('contact_notes', type=str, help='Contact Notes')

# Single Resources
class TabsContact(Resource):
	@marshal_with(resource_fields)
	def get(self, contact_id):
		abort_if_dne(Contact, contact_id)
		return db.session.query(Contact).get(contact_id)
		
class TabsProject(Resource):
	decorators = [login_required]
	@marshal_with(resource_fields)
	def get(self, project_id):
		abort_if_dne(Project, contact_id)
		return db.session.query(Project).get(project_id)

class TabsTimeEntry(Resource):
	@marshal_with(resource_fields)
	def get(self, contact_id):
		abort_if_dne(TimeEntry, time_entry_id)
		return db.session.query(TimeEntry).get(time_entry_id)


# Collections

class ContactList(Resource):
	decorators = [login_required]
	@marshal_with(resource_fields)
	def get(self):
		return db.session.query(Contact).all()
	@marshal_with(resource_fields)
	def post(self):
		args = parser.parse_args()
		nc = Contact()
		nc.name  = args['contact_name']
		nc.email = args['contact_email']
		nc.notes = args['contact_notes']
		db.session.add(nc)
		db.session.commit()
		return nc , 201
	@marshal_with(resource_fields)
	def put(self):
		args = parser.parse_args()
		contact = db.session.query(Contact).first()
		contact.name = args['contact_name']
		db.session.flush
		return contact

class ProjectList(Resource):
	decorators = [login_required]
	@marshal_with(resource_fields)
	def get(self):
		return db.session.query(Project).all()

class TimeEntryList(Resource):
	decorators = [login_required]
	@marshal_with(resource_fields)
	def get(self):
		return db.session.query(TimeEntry).all()


# Setup the API resource routing here
api.add_resource(TabsContact,  '/contact/<contact_id>')
api.add_resource(TabsProject,  '/projects/<project_id>')
api.add_resource(TabsTimeEntry,'/time_entries/<time_entry_id>')
api.add_resource(ContactList,  '/contacts')
api.add_resource(ProjectList,  '/projects')
api.add_resource(TimeEntryList,  '/time_entries')

