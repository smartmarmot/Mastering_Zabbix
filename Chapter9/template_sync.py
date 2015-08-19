#!/usr/bin/python

from pyzabbix import ZabbixAPI

rootUser = "Admin"
rootPwd = "zabbix"
rootUrl = "http://localhost/zabbix"

nodefile = "nodes.csv"
importRules = {"templates": {"createMissing": 'true', 
                             "updateExisting": 'true'},
               "templateLinkage": {"createMissing": 'true'},    
               "templateScreens": {"createMissing": 'true', 
                                   "updateExisting": 'true'}
              }

with open(nodefile, 'r') as f:
	nodes = f.readlines()

rootzh = ZabbixAPI(rootUrl)
rootzh.login(user=rootUser, password=rootPwd)

templates = rootzh.template.get(output=['templateid'])
tlist = []
for t in templates:
	tlist.append(t['templateid'])	

exports = rootzh.configuration.export(format="json", options={"templates": tlist})

for node in nodes:
	(name, url, usr, pwd) = node.rstrip('\n').split(";")
	nzh = ZabbixAPI(rootUrl)
	nzh.login(user=rootUser, password=rootPwd)
	result = nzh.confimport(format="json", rules=importRules, source=exports)
	print(result)
	nzh.user.logout()
	print( url + " " + usr )
