import networkx as nx
from pyzabbix import ZabbixAPI
dot_file="/tmp/total.dot"
username="Admin"
password="zabbix"
width = 800
height = 600
mapname = "my_network"
ELEMENT_TYPE_HOST = 0
ELEMENT_TYPE_MAP = 1
ELEMENT_TYPE_TRIGGER = 2
ELEMENT_TYPE_HOSTGROUP = 3
ELEMENT_TYPE_IMAGE = 4
ADVANCED_LABELS = 1
LABEL_TYPE_LABEL = 0
icons = {
    "router": 23,
    "cloud": 26,
    "desktop": 27,
    "laptop": 28,
    "server": 29,
    "sat": 30,
    "tux": 31,
    "default": 40,
}
colors = {
    "purple": "FF00FF",
    "green": "00FF00",
    "default": "00FF00",
}
def api_connect():
    zapi = ZabbixAPI("http://127.0.0.1/zabbix/")
    zapi.login(username, password)
    return zapi

def host_lookup(hostname):
    hostid = zapi.host.get({"filter": {"host": hostname}})
    if hostid:
        return str(hostid[0]['hostid'])
G=nx.read_dot(dot_file)
pos = nx.graphviz_layout(G)
positionlist=list(pos.values())
maxpos=map(max, zip(*positionlist))
for host, coordinates in pos.iteritems():
   pos[host] = [int(coordinates[0]*width/maxpos[0]*0.95-coordinates[0]*0.1), int((height-coordinates[1]*height/maxpos[1])*0.95+coordinates[1]*0.1)]
nx.set_node_attributes(G,'coordinates',pos)
selementids = dict(enumerate(G.nodes_iter(), start=1))
selementids = dict((v,k) for k,v in selementids.iteritems())
nx.set_node_attributes(G,'selementid',selementids)
nx.set_node_attributes(G,'selementid',selementids)
map_params = {
    "name": mapname,
    "label_type": 0,
    "width": width,
    "height": height
}
element_params=[]
link_params=[]
zapi = api_connect()
for node, data in G.nodes_iter(data=True):
    # Generic part
    map_element = {}
    map_element.update({
            "selementid": data['selementid'],
            "x": data['coordinates'][0],
            "y": data['coordinates'][1],
            "use_iconmap": 0,
            })
Check if we have the hostname
    if "hostname" in data:
        map_element.update({
                "elementtype": ELEMENT_TYPE_HOST,
                "elementid": host_lookup(data['hostname'].strip('"')),
                "iconid_off": icons['server'],
                })
    else:
        map_element.update({
            "elementtype": ELEMENT_TYPE_IMAGE,
            "elementid": 0,
        })
We sets label for images
    if "label" in data:
        map_element.update({
            "label": data['label'].strip('"')
        })
    if "zbximage" in data:
        map_element.update({
            "iconid_off": icons[data['zbximage'].strip('"')],
        })
    elif "hostname" not in data and "zbximage" not in data:
        map_element.update({
            "iconid_off": icons['default'],
        })

    element_params.append(map_element)

nodenum = nx.get_node_attributes(G,'selementid')
for nodea, nodeb, data in G.edges_iter(data=True):
    link = {}
    link.update({
        "selementid1": nodenum[nodea],
        "selementid2": nerodenum[nodeb],
        })

    if "color" in data:
        color =  colors[data['color'].strip('"')]
        link.update({
            "color": color
        })
    else:
        link.update({
            "color": colors['default']
        })

    if "label" in data:
        label =  data['label'].strip('"')
        link.update({
            "label": label,
        })

    link_params.append(link)

# Join the prepared information
map_params["selements"] = element_params
map_params["links"] = link_params
map=zapi.map.create(map_params)
