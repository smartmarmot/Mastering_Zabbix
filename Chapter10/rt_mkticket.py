#!/usr/bin/python2

from pyzabbix import ZabbixAPI
from rtkit.resource import RTResource
from rtkit.authenticators import CookieAuthenticator
from rtkit.errors import RTResourceError
import sys
import re

rt_url = sys.argv[1]
api_url = rt_url + "/REST/1.0/"
trigger_name = sys.argv[2]
message= sys.argv[3]

event_url = re.findall(r'^Event: (.+)$', message, re.MULTILINE)[0]
severity = re.findall(r'^Trigger severity: (.+)$', message, re.MULTILINE)[0]
hosts = re.findall(r'^Host: (.+)$', message, re.MULTILINE)
items = re.findall(r'^Item: (.+)$', message, re.MULTILINE)
lines = re.findall(r'^(?!(Host:|Event:|Item:|Trigger severity:))(.*)$', message, re.MULTILINE)
desc = '\n '.join([y for (x, y) in lines])

priorities = {
	'Not classified': 0,
	'Information': 20,
	'Warning': 40,
	'Average': 60,
	'High': 80,
	'Disaster': 100 }

queue_id = 3

ticket_content = {
	'content': {
		'Queue': queue_id,
		'Subject': trigger_name,
		'Text': desc,
		'Priority': priorities[severity],
		'CF.{Hosts}': ','.join(hosts),
		'CF.{Items}': ','.join(items),
		'CF.{Trigger}': trigger_name
	}
}

print(event_url)
links = {
	'content': {
		'RefersTo': '{}'.format(event_url)
	}
}

rt = RTResource(api_url, 'root', 'password', CookieAuthenticator)
ticket = rt.post(path='ticket/new', payload=ticket_content,)
(label,ticket_id) = ticket.parsed[0][0]
refers = rt.post(path=ticket_id + '/links', payload=links,)

event_id = re.findall(r'eventid=(\d+)', event_url)[0]

ticket_url = rt_url + 'Ticket/Display.html?id=' + ticket_id.split('/')[1]
print(ticket_url)
zh = ZabbixAPI('http://localhost/zabbix')
zh.login(user='Admin', password='zabbix')
ack_message = 'Ticket created.\n' + ticket_url
zh.event.acknowledge(eventids=event_id, message=ack_message)
 
