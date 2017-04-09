#!/usr/bin/env python

import os
import sys
import json
import boto3
import argparse
import subprocess
from subprocess import PIPE

class WinEc2Inventory(object):
	def empty_inventory(self):
		return {"_meta" : {"hostvars" : {}}}
	
	def __init__(self):
		self.inventory = {}
		self.read_cli_args()
		
		self.pem_key = 'path-to-pem'

		self.inventory = self.build_inventory()
		print json.dumps(self.inventory)

	def find(self):
		session = boto3.Session(profile_name='default')
		aws = session.client('ec2')
		instances = aws.describe_instances(
			Filters = [
				{
					'Name': 'platform',
					'Values':[
						'windows'
					]
				}
			]
		)

		return instances

	def build_inventory(self):
		hosts = self.find()

		list = {
			'group': {
				'hosts':[],
				'vars': {
					'ansible_user': 'Administrator',
					'ansible_port': '5986',
					'ansible_connection': 'winrm',
					# The following is necessary for Python 2.7.9+ when using default WinRM self-signed certificates:
					"ansible_winrm_server_cert_validation": "ignore"
				}
			},
			'_meta':{
				'hostvars':{

				}
			}
		}

		for reservations in hosts.get('Reservations'):
			for instance in reservations.get('Instances'):
				instance_id = instance.get('InstanceId')
				private_dns = instance.get('PrivateDnsName')

				if instance.get('KeyName') == 'ci-validation':
					get_pw_cmd = 'aws ec2 get-password-data --instance-id %s --priv-launch-key %s' % (instance_id, self.pem_key)
					get_pw = subprocess.Popen(get_pw_cmd, stdout=PIPE, stderr=PIPE, shell=True)
					out, err = get_pw.communicate()
					if err:
						print("Error Decrypting Keys: %s" % err)
						sys.exit(1)
					pw = json.loads(out)
					passwd = pw.get('PasswordData')
				else:
					 passwd = 'null'

				list['group']['hosts'].append('\'' + private_dns + '\'')
				#list['_meta'][private_dns] = "{'%s': 'ansible_password': '%s'}" % (private_dns, passwd)



		return list

	def read_cli_args(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('--list', action = 'store_true')
		parser.add_argument('--host', action = 'store')
		self.args = parser.parse_args()

WinEc2Inventory()