#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import os
import xml.dom.minidom
import argparse
# import gitlab
import glob
import sys

from datetime import datetime
from pyzabbix import ZabbixAPI, ZabbixAPIException
# from setuptools import setup, find_packages
from sys import exit


class Bgcolors:
    def __init__(self):
        self.get = {
            'HEADER': '\033[95m',
            'OKBLUE': '\033[94m',
            'OKGREEN': '\033[92m',
            'WARNING': '\033[93m',
            'FAIL': '\033[91m',
            'ENDC': '\033[0m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m'
        }


def login_to_zabbix(z_host, z_user, z_password):
    # You can use the connection__timeout
    connection__timeout = 45
    # Verify SSL
    verify__ssl = False
    # Connect to zabbix-server
    zapi = ZabbixAPI(z_host, timeout=connection__timeout)
    zapi.session.verify = verify__ssl
    if not verify__ssl:
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    zapi.login(z_user, z_password)
    zapi.session.auth = (z_user, z_password)
    # You can re-define connection__timeout after
    zapi.timeout = connection__timeout
    return zapi


def get_template(z_host, z_user, z_password, template):
    zapi = login_to_zabbix(z_host, z_user, z_password)
    get__template = zapi.template.get(filter={"name": template}, output=['templateid', 'name'])
    return get__template


def export_template(z_host, z_user, z_password, dir_path, template):
    zapi = login_to_zabbix(z_host, z_user, z_password)
    get_template_name = get_template(template)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    template_id = get_template_name[0]['templateid']
    template_name = get_template_name[0]['name']
    rules = {
        "options": {
            "templates": [template_id]
        },
        "format": "xml"
    }
    template_name_out = dir_path + '/' + template_name + '.xml'
    result = zapi.do_request('configuration.export', rules)
    template = xml.dom.minidom.parseString(result['result'].encode('utf-8'))
    date = template.getElementsByTagName("date")[0]
    # We are backing these up to git, steralize date so it doesn't appear to change
    # each time we export the templates
    date.firstChild.replaceWholeText('1970-01-01T01:01:01Z')
    try:
        f = open(template_name_out, 'wb')
        f.write(template.toprettyxml().encode('utf-8'))
        f.close()
        print (template_name + '.xml', 'file has been created')
    except ValueError:
        print ('I cant write to file: ', ValueError)

    return export_template


def get_templates(z_host, z_user, z_password):
    templates = []
    zapi = login_to_zabbix(z_host, z_user, z_password)
    get__templates = zapi.template.get(output=['templateid', 'name'])
    for template in get__templates:
        templates.append(template)
    return templates


def export_templates(z_host, z_user, z_password, dir_path):
    zapi = login_to_zabbix(z_host, z_user, z_password)
    templates = get_templates(z_host, z_user, z_password)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    for template in templates:
        template_id = template['templateid']
        template_name = template['name']

        template_name_out = dir_path + '/' + template_name + '.xml'
        result = zapi.configuration.export(
            options={"templates": [template_id]},
            format='xml'
        )
        template = xml.dom.minidom.parseString(result.encode('utf-8'))
        date = template.getElementsByTagName("date")[0]
        # We are backing these up to git, steralize date so it doesn't appear to change
        # each time we export the templates
        date.firstChild.replaceWholeText('1970-01-01T01:01:01Z')
        try:
            f = open(template_name_out, 'wb')
            f.write(template.toprettyxml().encode('utf-8'))
            f.close()
            print (template_name + '.xml', 'file has been created')
        except ValueError:
            print('I cant write to file')

    return export_templates


def import_templates(z_host, z_user, z_password, dir_path, templates):
    global files
    zapi = login_to_zabbix(z_host, z_user, z_password)

    rules = {
        'applications': {
            'createMissing': 'true',
            'updateExisting': 'true'
        },
        'discoveryRules': {
            'createMissing': 'true',
            'updateExisting': 'true'
        },
        'graphs': {
            'createMissing': 'true',
            'updateExisting': 'true'
        },
        'groups': {
            'createMissing': 'true'
        },
        'hosts': {
            'createMissing': 'true',
            'updateExisting': 'true'
        },
        'images': {
            'createMissing': 'true',
            'updateExisting': 'true'
        },
        'items': {
            'createMissing': 'true',
            'updateExisting': 'true'
        },
        'maps': {
            'createMissing': 'true',
            'updateExisting': 'true'
        },
        'screens': {
            'createMissing': 'true',
            'updateExisting': 'true'
        },
        'templateLinkage': {
            'createMissing': 'true',
            'updateExisting': 'true'
        },
        'templates': {
            'createMissing': 'true',
            'updateExisting': 'true'
        },
        'templateScreens': {
            'createMissing': 'true',
            'updateExisting': 'true'
        },
        'triggers': {
            'createMissing': 'true',
            'updateExisting': 'true'
        },
    }
    if templates == 'all':
        files = glob.glob(dir_path + "/" + "*.xml")
    else:
        for template in templates:
            files = glob.glob(str(dir_path) + "/" + str(template) + ".xml")
    for f in files:
        with open(f, 'r') as file:
            template = file.read()
            try:
                zapi.confimport('xml', template, rules)
            except ZabbixAPIException as e:
                print(e)
    return import_templates


def export_groups(z_host, z_user, z_password):
    file_out = 'exported_groups.txt'
    if os.path.isfile(file_out):
        os.remove(file_out)
    zapi = login_to_zabbix(z_host, z_user, z_password)
    get__groups = zapi.hostgroup.get(output=['groupid', 'name'])
    try:
        for group in get__groups:
            f = open(file_out, 'a')
            f.write(str(group['name'] + '\n'))
            f.close()
        print("All groups has been exported to %s!" % file_out)
    except ValueError:
        print('I cant write to file')

    return export_groups


def export_autodiscovery_rules(z_host, z_user, z_password):
    file_out = 'exported_autodiscovery_rules.txt'
    if os.path.isfile(file_out):
        os.remove(file_out)
    zapi = login_to_zabbix(z_host, z_user, z_password)
    get__actions = zapi.action.get(selectOperations='extend', selectFilter='extend', filter={"eventsource": 2})
    try:
        for action in get__actions:
            print (action)
            # f = open(file_out, 'a')
            # f.write(json.loads(action))
            # f.close()
        # print("All autodiscovery rules has been exported to %s!" % file_out)
    except TypeError:
        print('I cant write to file')

    return export_autodiscovery_rules


def main():
    start__time = time.time()

    parser = argparse.ArgumentParser(prog='python3 script_name.py -h',
                                     usage='python3 script_name.py {ARGS}',
                                     add_help=True,
                                     prefix_chars='--/',
                                     epilog='''created by Vitalii Natarov''')
    parser.add_argument('--version', action='version', version='v1.0.0')
    parser.add_argument('--t', '--template', nargs='+', dest='template', help='Indicate a template(s)', default='all')
    parser.add_argument('--d', '--dir', dest='templates_dir', help='Indicate a folder for template(s)',
                        default='exported_templates', metavar='folder')
    parser.add_argument('--zabbix-host', dest='zabbix_host', help='Zabbix host',
                        default=None)
    parser.add_argument('--zabbix-user', dest='zabbix_user', help='Zabbix user', default=None)
    parser.add_argument('--zabbix-password', dest='zabbix_password', help='Zabbix password of user',
                        default=None)

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--i', dest='imports', help='Import function', action='store_true')
    group.add_argument('--import', dest='imports', help='Import function', action='store_true')

    group2 = parser.add_mutually_exclusive_group(required=False)
    group2.add_argument('--e', dest='exports', help='Export function', action='store_true', default=argparse.SUPPRESS)
    group2.add_argument('--export', dest='exports', help='Export function', action='store_true')

    results = parser.parse_args()
    template = results.template
    templates_dir = results.templates_dir

    # host, login, password to connect to zabbix-server
    zabbix__host = results.zabbix_host
    zabbix__user = results.zabbix_user
    zabbix__password = results.zabbix_password

    if (zabbix__host is not None) and (zabbix__user is not None) and (zabbix__password is not None):
        zapi = login_to_zabbix(zabbix__host, zabbix__user, zabbix__password)
        zabbix__version = zapi.do_request('apiinfo.version')
        print(
            Bgcolors().get['OKGREEN'], "============================================================",
            Bgcolors().get['ENDC'])
        print(
            Bgcolors().get['OKGREEN'],
            'Zabbix Version:',
            zabbix__version['result'] + Bgcolors().get['ENDC'])
        print(
            Bgcolors().get['OKGREEN'],
            "============================================================",
            Bgcolors().get['ENDC'])
        if results.exports:
            print ('EXPORT function!')
            if template == 'all':
                export_templates(zabbix__host, zabbix__user, zabbix__password, templates_dir)
            else:
                export_template(zabbix__host, zabbix__user, zabbix__password, templates_dir, template)
            export_groups(zabbix__host, zabbix__user, zabbix__password)
            #export_autodiscovery_rules(zabbix__host, zabbix__user, zabbix__password)
        elif results.imports:
            print('IMPORT function')
            import_templates(zabbix__host, zabbix__user, zabbix__password, templates_dir, template)
        else:
            print('Please add [--e] for export or [--i] for import')
            print('For help, use: script_name.py -h')
            exit(0)
    else:
        print('Please add [--zabbix-host] or [--zabbix-user] or [--zabbix-password]')
        print('For help, use: script_name.py -h')
        exit(0)

    end__time = round(time.time() - start__time, 2)
    print("--- %s seconds ---" % end__time)

    print(
        Bgcolors().get['OKGREEN'], "============================================================",
        Bgcolors().get['ENDC'])
    print(
        Bgcolors().get['OKGREEN'], "==========================FINISHED==========================",
        Bgcolors().get['ENDC'])
    print(
        Bgcolors().get['OKGREEN'], "============================================================",
        Bgcolors().get['ENDC'])


if __name__ == '__main__':
    main()