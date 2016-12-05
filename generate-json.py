import urllib2
import sys, os
import getpass
import ssl, base64
import re
import simplejson, json 	# each package has its advantages
from pprint import pprint	# for testing

# Alex Van Heest -- Lehigh University's 2nd "LU Hacks," Dec 2-3, 2016

# The following is a series of methods written to manipulate the PI Web API's
# JSON files. These functions collect data from every building accessible from
# the "Hackathon" section of the Web API such that any additional buildings added
# will be collected as well. The data I looked at in particular includes only the
# measurements listed in the Elec (Shark) elements for each building, which
# provides concrete, constantly updated data.

# This script is to be run on the server side. We created a simple Apache server 
# using Amazon Web Services to accomplish this. This script interprets preexisting
# JSON files and creates new ones every minute (when run with the appropriate bash
# script) copying the new data to a static "current data" file.


# USAGE:: python testing-simple-gets.py

# Top level url:
top_level_url = "https://pi-core.cc.lehigh.edu/PIWEBAPI/"
# Cute username and password stuff with getpass()
username      = ""	# NOTE: in order to run properly, input Lehigh username here.
			# I've only deleted mine here for privacy purposes.
# print "Please enter password: "
password      = getpass.getpass() 	# NOTE: Using getpass to protect user's creds
					# when authenticating from a terminal.

# Energy units dictionary, for my reference:
units_dict        = {'Daily Energy Usage':'kilowatt hour', 'Daily Power Usage':'kilowatt', 'Watts Usage':'watt'}
units_dict_abbrev = {'Daily Energy Usage':'kWh', 'Daily Power Usage':'kW', 'Watts Usage':'W'}




# The following method will be used to make the process of making requests a 
# little easier. Returns a JSON object from the string grabbed at the given URL.
# NOTE: Two main steps were necessary to pin down how to authenticate the self-signed
# certificate: an encoded header and an SSL Context switch.
def get_json_for_url(desired_url):
	# Authenticate using a base64-encoded header.
	encoded_header_string = base64.b64encode('%s:%s' % (username, password))

	# This is the request-y stuff that works. Mostly trial and error
	# to get here, but now it works.
	try:
		gcontext  = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
		request   = urllib2.Request(desired_url)
		request.add_header("Authorization", "Basic %s" % encoded_header_string)
		response  = urllib2.urlopen(request, context=gcontext)
		page_text = response.read()
	except urllib2.HTTPError, e:
		# Added in mainly because I got tired of ugly output...
		print "ERROR: HTTP Error Code " + str(e.code) + " returned!!"
		exit(0)

	# Make sure there's no empty return value before returning:
	if page_text == None:
		print "Error: Requested URL returned no results"
		sys.exit(0)

	return simplejson.loads(page_text)




# This method will be used to store the current moment data as a new JSON file.
# This will ideally be stored on the server at the static "current" file and in
# a file labeled with a timestamp. Returns a JSON object.
def create_json_with_cur_data(daily_energy_dict, daily_power_dict, 
			watts_total_dict, data_timestamp_date, data_timestamp_hms):
	# Create a JSON file with the following format:
	'''
	{
		"Day":"2016-12-02",
		"HMS":"06:01:48",
		"BldgC":
			{
				"DEU": "7.97415290855e+22",
				"DPU": "3.4670231691e+21",
				"WU": "10671098896.4"
			}
		,
		"Sherman": 
			{
				"DEU": "7.97415290855e+22",
				"DPU": "3.4670231691e+21",
				"WU": "10671098896.4"
			}
		,
		"RauchChiller":
			{
				"DEU": "7.97415290855e+22",
				"DPU": "3.4670231691e+21",
				"WU": "10671098896.4"
			}
		,
		"Jordan":
			{
				"DEU": "7.97415290855e+22",
				"DPU": "3.4670231691e+21",
				"WU": "10671098896.4"
			}
		,
		"Varsity":
			{
				"DEU": "7.97415290855e+22",
				"DPU": "3.4670231691e+21",
				"WU": "10671098896.4"
			}
		,
		"Stadium": 
			{
				"DEU": "7.97415290855e+22",
				"DPU": "3.4670231691e+21",
				"WU": "10671098896.4"
			}
		,
		"Williams":
			{
				"DEU": "7.97415290855e+22",
				"DPU": "3.4670231691e+21",
				"WU": "10671098896.4"
			}
	}
	'''

	# Use a dictionary to create the JSON object. To be encoded below.
	main_dict = {}
	main_dict["Day"] = data_timestamp_date
	main_dict["HMS"] = data_timestamp_hms

	# For each building name, retrieve statistics and store in dictionary.
	for building_name in daily_energy_dict.keys():
		tmp_dict = {
			"DEU": daily_energy_dict[building_name],
			"DPU": daily_power_dict[building_name],
			"WU": watts_total_dict[building_name]
		}
		main_dict[building_name] = tmp_dict

	# Return as a JSON object.
	return json.JSONEncoder().encode(main_dict)



# Here is a simple method used to write the new data to the two output
# files: the "current" file and that given by a timestamp. (NOTE: due to
# the fact that only circa-hourly data was collected, no date portion of
# the timestamp is included in file name.) Returns output_filename for use
# by other functions.
def write_json_to_file(json_dumped_object, output_filename):
	# Create timestamped file.
	ofile = open(output_filename, 'w')
	simplejson.dump(json_dumped_object, ofile)
	ofile.close()

	# Create "current" file.
	ofile = open("json/power_data_current.json", 'w')
	simplejson.dump(json_dumped_object, ofile)
	ofile.close()

	# Return output_filename (for timestamped file)
	return output_filename



# Here is a method used in tandem with write_json_to_file that corrects
# some weird issues that happen with the file output. Using regex, it
# removes opening and closing quotes (and for a time removed bizarre \'s).
# One future addition to this would be to figure out why it made these
# weird errors while writing to the files, but since this was for a hackathon
# and time was running out, I made a simple fix here after exhausting all other
# avenues.
def fix_json_file(output_filename):
	# Open new file
	with open(output_filename, 'r') as fix_file:
		for line in fix_file:
			json_line = line

	# Fix file, sigh
	#json_line = json_line.replace("\\","")
	json_line = json_line.replace('^"',"")
	json_line = json_line.replace('"$',"")

	# Re-write file to original name.
	with open(output_filename, 'w') as fix_file:
		fix_file.write(simplejson.loads(json_line))



# Simple method used once or twice to open a JSON file at a given filepath
# and display with pprint, which makes it look nice. I used this to make sure
# the JSON objects I was created were actually valid, and it helped identify
# some strange errors.
def test_json_file(output_filename):
	with open(output_filename) as data_file:    
		data = json.load(data_file)
		pprint(data)



# This method simply builds a static JSON object with relevant units and 
# square-footage data for each building. This static json file wasn't used
# in the application, but in future applications, it would be more complex and
# allow for additions to provided data-types and new buildings added. Returns
# output filename for potential use by other methods.
def build_static_json():
	# Constant output filename.
	output_filename = "static.json"

	# Includes unit values for each measure. ft^2 is estimated with
	# a Google Maps application online.
	tmp_dict = {
		"DEU": "kWh",
		"DPU": "kW",
		"WU": "W",
		"BldgC": 21250,
		"Jordan": 25725,
		"RauchChiller": 14700,
		"Sherman": 17500,
		"Stadium": 354000,
		"Varsity": 60000,
		"Williams": 25000
	}

	# Call write_json_to_file to do exactly that.
	write_json_to_file(json.JSONEncoder().encode(tmp_dict), output_filename)

	# Return the static filename for use by other methods.
	return output_filename


# MAIN:
# Below holds links to the major buildings provided in the Hackathon element
hackathon_asset_directory_url = top_level_url + "assetdatabases/D0WsSLFDAMCEi9V3Cd3PWPog4vFJC1em3kSuT8Cflj_UUQUEktREFUQVxIQUNLQVRIT04/elements"

# Retrieve JSON object for all building elements.
json_text = get_json_for_url(hackathon_asset_directory_url)
items = json_text.get('Items')

# Collect elements-for-each-building urls.
elements_urls = []
for item in items:
	elements_urls.append(str(item.get('Links').get('Elements')))

# Now we've got a list of URLs that holds the elements of each building.
# The next step is to grab the Elec Shark elements of these elements.
# The following is a dictionary that takes building names as keys and
# stores their respective URLs as vals:
summary_urls = {}
substr_shark_elec = "Elec (Shark)" 	# naming convention for each desired element

# Rather complex series of for-each loops that will get the URLs for 
# the summary portions for each building, to be stored in above dictionary.
for e_url in elements_urls:
	e_json = get_json_for_url(e_url)
	cur_items = e_json.get('Items')
	for new_url in cur_items:
		cur_name = new_url.get('Name')
		if substr_shark_elec in cur_name:
			end_index = cur_name.find(substr_shark_elec)
			cur_building = cur_name[0:end_index-1].replace("Bldg-C","BldgC")
			summary_urls[cur_building] = new_url.get('Links').get('SummaryData')

# TEST: Make sure that the key-val pairs are working:
# for key in summary_urls.keys():
# 	print key + ": " + summary_urls[key]

# Okay, now we have the URLs to the summary data.
# Now it's time to parse the summary data for each building

# The following is a set of dictionary to store data from each category:
daily_energy_dict = {}
daily_power_dict  = {}
watts_total_dict  = {}
data_timestamp_date = ""
data_timestamp_hms  = ""

# Another rather complex set of for-each loops that collects power usage data
# from each found JSON object. This will populate the above dictionaries with
# data for any building provided under the original HACKATHON umbrella, so it's
# meant to be sustainable. The main additions that would need to be made are
# fixes for the energy/power units collected if more data were given.
for building_name, s_url in summary_urls.iteritems():
	s_json = get_json_for_url(s_url)
	cur_items = s_json.get('Items')
	for power_stat in cur_items:
		power_stat_items = power_stat.get('Items')
		power_stat_item_vals = power_stat_items[0].get('Value')
		data_timestamp_date = power_stat_item_vals.get('Timestamp')[0:10]
		data_timestamp_hms  = power_stat_item_vals.get('Timestamp')[11:19]
		psiv_final_value = power_stat_item_vals.get('Value')
		if "e" in str(psiv_final_value):
			index_of_e = str(psiv_final_value).index('e')
			psiv_final_value = str(psiv_final_value)[:index_of_e]
		# Conditional to handle three desired power statistics:
		if power_stat.get('Name') == "Daily Energy":
			daily_energy_dict[building_name] = psiv_final_value
		elif power_stat.get('Name') == "Daily Power":
			daily_power_dict[building_name] = psiv_final_value
		elif power_stat.get('Name') == "Watts Total":
			watts_total_dict[building_name] = psiv_final_value
		else:
			temp = 1 	# catch weird cases / unknown data types, 
						# should be none though at least yet though

# TEST: Make sure every building's units are indeed collected:
# print "Daily Energy Usage"
# for bldng_name, energy_usage in daily_energy_dict.iteritems():
# 	print "{:<15}\t{:}".format(str(bldng_name), str(energy_usage))
# print "\n\n\n\n\n\n\nDaily Power Usage"
# for bldng_name, power_usage in daily_power_dict.iteritems():
# 	print "{:<15}\t{:}".format(str(bldng_name), str(power_usage))
# print "\n\n\n\n\n\n\nWatts Usage"
# for bldng_name, power_usage in watts_total_dict.iteritems():
# 	print "{:<15}\t{:}".format(str(bldng_name), str(power_usage))

# Quick fix: let's make this EST, not UTC+0:
dthms_list = data_timestamp_hms.split(":")
dthms_list[0] = str(int(dthms_list[0]) - 5)
if len(dthms_list[0]) == 1:
	dthms_list[0] = "0" + dthms_list[0]
data_timestamp_hms = dthms_list[0] + "" + dthms_list[1]

# Build the JSON file with collected data, to be stored on server somehow
new_json = create_json_with_cur_data(daily_energy_dict, daily_power_dict, watts_total_dict, data_timestamp_date, data_timestamp_hms)

# Write to file, using timestamp
output_filename = "json/power_data_" + str(data_timestamp_hms) + ".json"
op_filename = write_json_to_file(new_json, output_filename)

# Fix weird formatting issues (poorman's time-constraint band-aid approach...)
fix_json_file(op_filename)
fix_json_file("json/power_data_current.json")

# TEST: Check whether or not JSON file is written properly:
#test_json_file(op_filename)

# Create static json file, to be referenced as a constant upload to server.
static_json_filename = build_static_json()
fix_json_file(static_json_filename)
