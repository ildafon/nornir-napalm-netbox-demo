#!./venv/bin/python

import re
import os
import textfsm
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result
from nornir import InitNornir
from netbox import NetBox
from pprint import pprint

# DEBUGGING
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
# logging.debug('A debug message!')


# Init
nr = InitNornir(config_file="./config.yaml")
tmpl_path = './templates/'
out_path = './data/'
hosts = {}
ips = {}
inventory = {}


def load_hosts():
    hosts = {}
    ips = {}
    template = open("./templates/hosts.textfsm")

    hosts_file = open("./hosts", encoding='utf-8')
    raw_data = hosts_file.read()
    hosts_file.close()

    re_table = textfsm.TextFSM(template)
    fsm_result = re_table.ParseText(raw_data)
    # import ipdb; ipdb.set_trace()
    for i in fsm_result:
        hosts[i[0]] = i[1]
        ips[i[1]] = i[0]
    return (hosts,ips)


def load_routerdb(hosts, ips):
    inventory = {}
    template = open("./templates/routerdb.textfsm")

    routerdb_file = open("./router.db", encoding='utf-8')
    raw_data = routerdb_file.read()
    routerdb_file.close()

    re_table = textfsm.TextFSM(template)
    fsm_result = re_table.ParseText(raw_data)

    for i in fsm_result:
        try:
           ip = hosts[i[0]]
        except:
            continue

        inventory[i[0]] = {
            'ip': ip,
            'type': i[1],
            'state': i[2]
        }

    return inventory




def get_hostname(ip_address):
    return ips[ip_address]


def get_ip(hostname):
    return hosts[hostname]


def get_command_output(command, devices, use_textfsm):
    result = devices.run(
        name=command,
        task=networking.netmiko_send_command,
        command_string=command,
        use_textfsm=use_textfsm
    )
    command_result = {}
    for host in result.keys():
        if result[host][0].failed:
            command_result[host] = ''
            continue
        command_result[host] = result[host][0].result
        logging.info("Command output from device %s: %s" % (host, command_result[host]))
    return command_result


def parse_result(cmd_output_dict, template, command):
    parse_result_dict = {}

    # try:
    #    template = open(tmpl_path + tmpl_name, "r")
    # except:
    #    logging.error("Error! Template not found!: %s" % tmpl_path + tmpl_name)
    #    exit(1)
    for host in cmd_output_dict.keys():
        re_table = textfsm.TextFSM(template)
        parse_result_dict[host] = re_table.ParseText(cmd_output_dict[host])
        logging.info("Parsing result of command output %s: %s" % (command, parse_result_dict[host]))
    return parse_result_dict


def save_csv_table(template, parsed_result_dict, command):
    re_table = textfsm.TextFSM(template)
    for host in parsed_result_dict.keys():
        outfile = out_path + "_".join(command.split()) + "_" + host + ".csv"

        with open(outfile, "w+") as f:
            for s in re_table.header:
                f.write("%s;" % s)
            f.write("\n")

            for row in parsed_result_dict[host]:
                for el in row:
                    f.write("%s;" % el)
                f.write("\n")


def save_parsed_to_csv(output, command):
    for host in output.keys():
        outfile = out_path + "_".join(command.split()) + "_" + host + ".csv"

        with open(outfile, "w+") as f:
            for key in output[host][0].keys():
                f.write("%s;" % key)
            f.write("\n")

            for row in output[host]:
                for val in row.values():
                    f.write("%s;" % val)
                f.write("\n")


if __name__ == "__main__":
    hosts, ips = load_hosts()
    inventory = load_routerdb(hosts,ips)
    os.environ["NET_TEXTFSM"] = "./ntc-templates/templates"
    command_list = ['show vlan', 'show vrf']
    role = 'PE'
    model = '7606'
    # tmpl_name = 'junos_show_ip_route.textfsm'

    # try:
    #    template = open(tmpl_path + tmpl_name, "r")
    # except:
    #    logging.error("Error! Template not found!: %s" % tmpl_path + tmpl_name)
    #    exit(1)

    devices = nr.filter(role=role, model=model)
    logging.info(devices.inventory.get_inventory_dict())
    for command in command_list:
       output = get_command_output(command, devices, use_textfsm=True)
       save_parsed_to_csv(output,command)
    #save_json_to_csv(output, command)

    # cmd_output_dict = get_command_result_dict(command, devices)
    # cmd_parsed_dict = ntc_parse_output(cmd_output_dict, command)

    # parsed_result_dict = parse_cmd_result_dict(cmd_output_dict, template, command)
    # save_csv_table(template, parsed_result_dict, command)
