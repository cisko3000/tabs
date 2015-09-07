from flaskext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import validators
from models import Appointment, User

# You can customize the created form at creation.
# Here is an example of adding an extra validator to one of the fields
# AppointmentForm = model_form(Appointment, Form, field_args = {
#     'name' : {
#         'validators' : [validators.Length(max=10)]
#     }
# })

AppointmentForm = model_form(Appointment, Form)