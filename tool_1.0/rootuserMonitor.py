import boto3
from string import *
from ipwhois import IPWhois
import warnings


def getEvents(client):
	"""
	Looks up API activity events captured by CloudTrail in AWS account.
	– OUTPUT: Events(list)
	"""
	
	# rootuserEvent is a dictionary with  a key "Events" and a list as a value
	# the list has many subset of dictionaries for each event.
	rootuserEvent = client.lookup_events(
		LookupAttributes = [
			{
				'AttributeKey': 'Username',
				'AttributeValue': 'root'
			},
		],
	)

	return rootuserEvent["Events"]


def isRootuser(events):
	if len(events) > 0:
		return True
	else:
		False


def getActivities(events):
	"""
	- INPUT : root-user events (list)
	- OUTPUT: unique activities happened with root-user (set)
	"""
	activities = set()

	for i in range(len(events)):
		activities.add(events[i]["EventName"])

	return activities


def getActivitiesDatetime(events):
	"""
	- INPUT : root-user events (list)
	- OUTPUT: lastest time that activities was happened (datetime)
	"""
	datetime = set()

	for i in range(len(events)):
		datetime.add(events[i]["EventTime"])

	return max(datetime)


def getIPaddresses(events):
	"""
	- INPUT : root-user events (list)
	– OUTPUT: unique ip addresses of activities (list)
	"""
	ips_dict = {}

	for i in range(len(events)):
		ctEvents_str = events[i]["CloudTrailEvent"]
		ctEvents_lst = ctEvents_str.split(",")

		for item in ctEvents_lst:
			if "sourceIPAddress" in item:
				ips_dict[item] = 0

	ips_lst = []

	for key in ips_dict:
		ips_lst.append(key) # ips_lst = ['"sourceIPAddress":"str"', '"sourceIPAddress":"str"']

	ip_lst = []
	for item in ips_lst:
		for l in ascii_letters:
			item = item.replace(l, '')
		item = item.replace('"', '')
		item = item.replace(':', '')

		# this is a bandaid
		if item != '..':
			ip_lst.append(item) # ip_lst = ['str', 'str']

	return ip_lst


def lookupDomainName(ipaddrs):
	"""
	– INPUT : takes in one ip address (str)
	– OUTPUT: ipwhois result (dict)
	"""
	with warnings.catch_warnings():
		warnings.filterwarnings("ignore", category = UserWarning)

		obj = IPWhois(ipaddrs)
		ipInfo = obj.lookup_whois()

	return ipInfo


def getRootUserReport(events ,msg):
	print (" –––– WARNING!! Activities with root user detected! –––– \n")
	
	# Show the last time the activity with root user happened 
	print ("Last activity:\n\n", "   - ", getActivitiesDatetime(events), '\n')
	
	# Show types of activities 
	print ("Activity types:\n")
	for i in getActivities(events):
		print ("    - ", i)
	
	# Check where the access was happened using ip address 
	print ("\nThe root user access was attempted from:\n")
	ips = getIPaddresses(events) # ['str', 'str']
	print ("ips: ", ips)

	for ip in ips:
		result = lookupDomainName(ip)

		description = []
		for i in range(len(result['nets'])):
			description.append(result['nets'][i]['description'])

			print (ip, description)

	print (msg)


def main(events):

	# Rendering messages
	rootuserWarningMsg = "\nAWS encourages users not to use root user credentials to access AWS.\n" \
						 "Instead, create an IAM user. Check: \n" \
						 "\n    https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html\n"\
						 "\nfor more information.\n"
	 
	# Store events from CloudTrail associated with root-user
	eventList = getEvents(events)

	# Steps to take if there is activities detected with root-user
	if isRootuser(eventList):
		getRootUserReport(eventList, rootuserWarningMsg)

	else:
		print ("No root user related activities were found from past 90 days.")
