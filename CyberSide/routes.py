# Flask imports
from flask import redirect, url_for, render_template, request,session
# Database models imports
from .models import db, cyberside_user, login_manager
# Password hashing import
import bcrypt
# Flask-Login imports
import flask_login
from flask_login import login_user, login_required, logout_user, current_user
# Import app in a way to prevent circular imports
from flask import current_app as app
# Chat ids random string imports
import random
import string
# Date and Time import
from datetime import datetime
# Email Validation:
import re
# Import SocketIO file
from .socketz import *

# Import OS
import os
# Import shutil for copying images
from shutil import copyfile

#This file contains custom routes handling for the Metro2.0 project

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return render_template("error/404.html")

@app.route("/", methods=['GET', 'POST'])
def index():
	if not flask_login.current_user.is_authenticated:
		if 'user' in session:
			if session_user := metro_user.query.get(int(session['user'])):
				login_user(session_user)
				# session['bullets'] = session_user._balance
				# session['colorPalette'] = session_user.theme

		else:
			if request.method == "POST":
				# login part
				pass
			
			return render_template("home.html")

	if flask_login.current_user.is_authenticated:
	# 	if 'bullets' not in session:
	# 		session['bullets'] = flask_login.current_user._balance
	# 	if 'colorPalette' not in session:
	# 		session['colorPalette'] = flask_login.current_user.theme
		return render_template("home.html")

@app.route("/<name>")
@app.errorhandler(404)
def something(name):
	return render_template("error/404.html", url = name)
