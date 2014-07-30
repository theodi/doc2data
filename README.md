This is a simple Python utility to automatically convert a google docs spreadsheet into csv and json data. 

To configure:

Create a Google Docs spreadsheet with the following columns:

Then, copy sample-config to .config (with the ".") and edit with your Google username, password, and mailing address.

Licence
-------
This software comes without warrenty or guarentee and has been developed as an Open Data Institute labs project. If would like to contact us about the labs project please do not email, rather use the github issues tracker at http://github.com/theodi/doc2data

Execution
---------

Python doc2data.py 

Dependencies
------------

gdata for python, install with:

    easy_install gdata

	or
 
    apt-get install python-gdata 
