#!./venv/bin/python

import re
import os
import textfsm
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result
from nornir import InitNornir
from netbox import NetBox
from pprint import pprint
from texfsm_test  import load_hosts,load_routerdb,get_command_output

# DEBUGGING
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

tmpl_path = './templates/'
data_path = './data/'
nr = InitNornir(config_file="./config.yaml")
inventory = {}

def load_csv_data(command, hostname,):
    path = f"{data_path}{'_'.join(command.split())}_{hostname}.csv"
    result = []
    with open(path) as f:
        colons = f.readline().strip('\n').split(';')[:-1]

        for line in f:
            line = line.strip('\n').split(';')[:-1]
            result.append(
                dict(zip(colons,line))
            )
    return result

def load_network_data(command, hostname):
    device_ip = inventory[hostname]['ip']
    device = nr.filter(hostname = device_ip)
    logging.info(device.inventory.get_inventory_dict())
    command_result = get_command_output(command, device, True)
    return command_result

def is_data_insync(command, hostname):
    data_loaded = load_csv_data(command, hostname)
    data_from_node = load_network_data(command, hostname)

def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    shared_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
    same = set(o for o in shared_keys if d1[o] == d2[o])
    return added, removed, modified, same



if __name__ == "__main__":
    hosts,ips = load_hosts()
    inventory = load_routerdb(hosts,ips)
    os.environ["NET_TEXTFSM"] = "./ntc-templates/templates"
    hostname = 'TLC-RUES-PE03-01'
    command = 'show vrf'

    from_csv = load_csv_data(command,hostname)
    from_net = load_network_data(command,hostname)[hostname]
    import ipdb;ipdb.set_trace()
    if len(from_csv) != len(from_net):
        pprint(f"len of csv {len(from_csv)}, len of result from net {len(from_net)}")
        logging.critical("COMMAND RESULT DIFFER on DEVICE and LOADED!")