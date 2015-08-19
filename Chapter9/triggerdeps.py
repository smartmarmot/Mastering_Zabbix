#!/usr/bin/python
from pyzabbix import ZabbixAPI
zh = ZabbixAPI("http://127.0.0.1/zabbix")
zh.login(user="Admin", password="zabbix")


def gettriggername(triggerid=''):
	return zh.trigger.get(triggerids=triggerid, output=['description'])[0]['description']

tr = zh.trigger.get(selectDependencies="refer", expandData="1", output="refer")
dependencies = [(t['dependencies'], t['host'], t['triggerid']) for t in tr if t['dependencies'] != [] ]


outfile = open('trigdeps.gv', 'w')
outfile.write('digraph TrigDeps {\n')
outfile.write('graph[rankdir=LR]\n')
outfile.write('node[fontsize=10]\n')

for (deps, triggerhost, triggerid) in dependencies:
	triggername = gettriggername(triggerid)
	
	for d in deps:
		depname = gettriggername(d['triggerid'])
		dephost = d['host']
		edge = '"{}:\\n{}" -> "{}:\\n{}";'.format(dephost, depname, triggerhost, triggername)
		outfile.write(edge + '\n')

outfile.write('}\n')
outfile.close()
		
