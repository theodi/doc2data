#!/usr/bin/env python
#
#   odi-awards.py -- Takes content of google spreadsheet and outputs csv and json of select columns only
#
#  <davetaz@theodi.org> <phil.lang@theodi.org>
#  July 2014
#
# With thanks to <andy@payne.org> for the reference code, merry christmas!

import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service
import re, os, os.path
import ConfigParser
import sys
import csv
import json

# Read configuration
cfile = os.path.expanduser('.config')
if not os.path.isfile(cfile):
	print "Configuration file %s is missing!" % cfile
	sys.exit(1)

c = ConfigParser.ConfigParser()
c.read(cfile)
config = {}
for i in ('username', 'password', 'doc_name'):
	config[i] = c.get('general', i).strip()

# Connect to Google
# This is a comment in blue
gd_client = gdata.spreadsheet.service.SpreadsheetsService()
gd_client.email = config['username']
gd_client.password = config['password']
gd_client.source = 'theodi.org-summit-1'
gd_client.ProgrammaticLogin()

# Open CSV output
ofile = open('nominations.csv','wb')
writer = csv.writer(ofile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL)

# Query for the rows
# print "Reading rows...."
q = gdata.spreadsheet.service.DocumentQuery()
q['title'] = config['doc_name']
q['title-exact'] = 'true'
feed = gd_client.GetSpreadsheetsFeed(query=q)
assert(feed)
spreadsheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
feed = gd_client.GetWorksheetsFeed(spreadsheet_id)
worksheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
rows = gd_client.GetListFeed(spreadsheet_id, worksheet_id).entry

dups = {}

output_keys=['organisationname','website','twitterhandle','describetheorganisationbeingnominated']
titles={}
titles['organisationname'] = 'Organisation Name'
titles['website'] = 'Website'
titles['twitterhandle'] = 'Twitter'
titles['describetheorganisationbeingnominated'] = 'Description'

csv_output = []
for key in titles: 
	csv_output.append(titles[key])

json_output = {}
json_output["title"] = "ODI Summit 2014 Awards Nominations Data"
json_output["licence"] = "CC-BY-SA 4.0"
json_output["nominations"] = []

writer.writerow(csv_output)

for (count, row) in enumerate(rows):
	data = {}
	csv_output = []
	for key in row.custom:
		if row.custom[key].text and key in output_keys:
			csv_output.append(row.custom[key].text.strip())
			data[titles[key]] = row.custom[key].text.strip()
		elif key in output_keys:
			data[titles[key]] = ""
			csv_output.append("")

	json_output["nominations"].append(data)
	
	writer.writerow(csv_output)

ofile.close()
with open('nominations.json', 'wb') as outfile:
	json.dump(json_output, outfile)
