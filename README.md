TABS (Time And Billing System)
==============================
Flask based system for project time tracking and invoice creation
------------------------------------------------------------------
# Features
* Contacts, Projects, Time Entries
* Start/Stop Time Entry creation
* Paypal Invoice Creation
* Weekly Time Entries Summary

# Installation
1.  pull code
2.  install virtualenv "sudo apt-get virtualenv"
3.  ". env/bin/source" to activate virtual environment
4.  change into source directory and install requirements with "pip install -r requirements" 
5.  cp config.py to true_config.py and edit true_config.py with your own settings
6.  "python run.py" to run app

# Notes
The custom admin interface is still under construction. You can edit database records through flask-admin.
flask-admin view is accessible at "web.app.url.com/admin"
That is all!



