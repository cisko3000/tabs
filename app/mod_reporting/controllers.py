from flask import Blueprint, request, render_template, redirect, url_for
from flask.ext.login import login_required, current_user

from flask.ext.wtf import Form
from .. import db
from app.models import *

mod_reporting = Blueprint('reporting', __name__, url_prefix='/rep')

@mod_reporting.route('/index', methods=['GET'])
@login_required
def home():
	return render_template('reporting/home.html')