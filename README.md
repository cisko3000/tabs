TABS (Time And Billing System)
==============================
######Flask based system for project time tracking and invoice creation
------------------------------------------------------------------
# Bugs

# Features
* Contacts, Projects, Time Entries
* Start/Stop Time Entry creation
* Paypal Invoice Creation
* Weekly Time Entries Summary

# Installation
1.  pull code
2.  install virtualenv `sudo apt-get virtualenv`
3.  create virtual environment `virtualenv env` 
4.  activate virtual environment `. env/bin/source`
5.  change into tabs source directory and install requirements with `pip install -r requirements.txt`
6.  create true_config.py file `cp config.py to true_config.py`
7.  edit the database path in true_config.py file to where you want your database to be created
8.  `python run.py` to run app

# Notes
The custom admin interface is still under construction. You can edit database records through flask-admin.
flask-admin view is accessible at "web.app.url.com/admin"
That is all!



