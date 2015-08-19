#!/usr/bin/python
from pyzabbix import ZabbixAPI
import sys
import csv
from datetime import datetime
appname = sys.argv[1]
timeformat="%d/%m/%y %H:%M"

zh = ZabbixAPI("http://127.0.0.1/zabbix")
zh.login(user="Admin", password="zabbix")

aa = zh.application.get(output="shorten", filter={"name": [appname]})
items = zh.item.get(output="count", applicationids=[x['applicationid'] for x in aa])
triggers = zh.trigger.get(output="refer", itemids=[x['itemid'] for x in items])

events = zh.event.get(triggerids=[j['triggerid'] for j in triggers])

def gethostname(hostid=''):
	return zh.host.get(hostids=hostid, output=['host'])[0]['host']

def getitemname(itemid=''):
	return zh.item.get(itemids=itemid, output=['name'])[0]['name']

def gettriggername(triggerid=''):
	return zh.trigger.get(triggerids=triggerid, expandDescription="1", output=['description'])[0]['description']

eventstable = []
triggervalues = ['OK', 'problem', 'unknown']
for e in events:
	eventid = e['eventid']
	event = zh.event.get(eventids=eventid, 
			       selectHosts="refer", 
			       selectItems="refer",
			       selectTriggers="refer",
			       output="extend")
	host = gethostname(event[0]['hosts'][0]['hostid'])
	item = getitemname(event[0]['items'][0]['itemid'])
	trigger = gettriggername(event[0]['triggers'][0]['triggerid'])
	clock = datetime.fromtimestamp(int(event[0]['clock'])).strftime(timeformat)
	value = triggervalues[int(event[0]['value'])] 
	eventstable.append({"Host": host, "Item": item, "Trigger": trigger, "Status": value, "Time" : clock })
filename = "events_" + appname + "_" + datetime.now().strftime("%Y%m%d%H%M")
fieldnames = ['Host', 'Item', 'Trigger', 'Status', 'Time']
outfile = open(filename, 'w')
csvwriter = csv.DictWriter(outfile, delimiter=';', fieldnames=fieldnames)
csvwriter.writerow(dict((h,h) for h in fieldnames))
for row in eventstable:
     csvwriter.writerow(row)
outfile.close()
