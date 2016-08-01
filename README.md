TABS (Time And Billing System)
==============================
######Flask based system for project time tracking and invoice creation
------------------------------------------------------------------
# Bugs
TODO
implement calendar date range.

angular.js bugs
filter does not re calculate project.delta total


knockout.js bugs
Update project contacts menu (knockout.js interface only)
Add project doesn't work (knockout.js interface only)
Deselects project on start and stop (knockout.js interface only)



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
N/A


