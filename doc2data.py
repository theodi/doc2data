#!/usr/bin/env python
#
#  doc2data.py -- Takes content of google spreadsheet and outputs csv and json.
#
#  See sample config for usage and configuration
#
#  <davetaz@theodi.org> <phil.lang@theodi.org>
#  July 2014
#
#  With thanks to <andy@payne.org> for the reference code, merry christmas!
#

import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service
import re, os, os.path
import ConfigParser
import sys
import csv
import json

json_output = {}
title_map = {}

# Read configuration
cfile = os.path.expanduser('.config')
if not os.path.isfile(cfile):
	print "Configuration file %s is missing!" % cfile
	sys.exit(1)

c = ConfigParser.ConfigParser()
c.read(cfile)
config = {}
for i in ('username', 'password', 'doc_name', 'csv_file', 'json_file'):
	config[i] = c.get('general', i).strip()

options = c.options('dataset_metadata')
for option in options:
	json_output[option] = c.get('dataset_metadata',option).strip()

output_keys = False
try:
	selected_columns = c.get('options', 'selected_columns').strip()
	# NOT THE BEST WAY FIXME WITH PROPER CSV PARSING
	output_keys = selected_columns.split(",")
except: 
	pass

try:
	options = c.options('title_map')
	for key in options:
		title_map[key] = c.get('title_map',key).strip()
except:
	pass

titles = False

# Connect to Google
# This is a comment in blue
gd_client = gdata.spreadsheet.service.SpreadsheetsService()
gd_client.email = config['username']
gd_client.password = config['password']
gd_client.source = 'theodi.org-doc2data'
gd_client.ProgrammaticLogin()

# Open CSV output
ofile = open(config['csv_file'],'wb')
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

def getHeadingsFromRow(row):
	headings = []
	for key in row.custom:
		headings.append(key)
	return headings;

def getHeadingsFromConfig(output_keys,titles):
	if not titles:
		return output_keys
	return False;

def writeTitlesToCSV(titles,writer):
	csv_output = []
	for key in titles: 
		csv_output.append(titles[key])
	
	writer.writerow(csv_output)

def getTitles(headings,title_map):
	titles = {}
	for heading in headings:
		try:
			titles[heading] = title_map[heading]
		except:
			titles[heading] = heading
	return titles
	

headings_done = False;
json_output["rows"] = []
headings = getHeadingsFromConfig(output_keys,titles)
if headings:
	if not titles:
		titles = getTitles(headings,title_map)
	writeTitlesToCSV(titles,writer)
	headings_done = True;

for (count, row) in enumerate(rows):
	if not headings_done:
		headings = getHeadingsFromRow(row)
		titles = getTitles(headings,title_map)
		writeTitlesToCSV(titles,writer)
		output_keys = headings
		headings_done = True;
	data = {}
	csv_output = []
	for key in row.custom:
		if row.custom[key].text and key in output_keys:
			csv_output.append(row.custom[key].text.strip())
			data[titles[key]] = row.custom[key].text.strip()
		elif key in output_keys:
			data[titles[key]] = ""
			csv_output.append("")

	json_output["rows"].append(data)
	
	writer.writerow(csv_output)

ofile.close()
with open(config['json_file'], 'wb') as outfile:
	json.dump(json_output, outfile)
