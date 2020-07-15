#!./venv/bin/python

import re
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result
from nornir import InitNornir
from netbox import NetBox
from pprint import pprint

nr = InitNornir(config_file="./config.yaml")

nb_url, nb_token, ssl_verify = nr.config.inventory.options.values()
nb_host = re.sub("^.*//|:.*$", "", nb_url)

netbox = NetBox(host=nb_host, port=32768, use_ssl=True, auth_token=nb_token)
nb_interfaces = netbox.dcim.get_interfaces()

pprint(nb_interfaces)


