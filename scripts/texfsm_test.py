#!./venv/bin/python

import re

import textfsm
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result
from nornir import InitNornir
from netbox import NetBox
from pprint import pprint

# DEBUGGING
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
#logging.debug('A debug message!')

#Init
nr = InitNornir(config_file="./config.yaml")
tmpl_path = './templates/'
out_path = './data/'

def get_command_result_dict(command, devices):
    command_result = devices.run(
        name=command,
        task= networking.netmiko_send_command,
        command_string=command
    )
    command_result_dict = {}
    for host in command_result.keys():
        if command_result[host][0].failed:
            command_result_dict[host] = ''
            logging.error("Failed to get command output %s from device $s" % (command, host))
            continue
        command_result_dict[host] = command_result[host][0].result
        logging.info("Command output from device %s: %s" % (host, command_result_dict[host]))

    return command_result_dict

def parse_cmd_result_dict(cmd_output_dict, template, command):
    parse_result_dict = {}

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

if __name__ == "__main__":
    command = 'show vrf'
    role = 'pe'
    tmpl_name = 'cisco_show_vrf.textfsm'

    try:
        template = open(tmpl_path + tmpl_name, "r")
    except:
        logging.error("Error! Template not found!: %s" % tmpl_path + tmpl_name)
        exit(1)

    devices = nr.filter(role=role)

    cmd_output_dict = get_command_result_dict(command, devices)
    parsed_result_dict = parse_cmd_result_dict(cmd_output_dict, template, command)
    save_csv_table(template, parsed_result_dict, command)
