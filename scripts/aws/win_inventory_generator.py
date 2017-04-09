#!/usr/bin/env python

"""
	I'm a fan of automation.
	Let's get windows inventory going for ya
"""

import os
import boto3
import json
import sys
import subprocess
import argparse
from subprocess import PIPE

hosts = []
environments =[]
inventory_list = []

class Generator(object):
	def __init__(self):
		parser = argparse.ArgumentParser(description='Windows Inventory Builder')
		parser.add_argument('--pem')
		parser.add_argument('--region')
		parser.add_argument('--inventory')
		parser.add_argument('--profile')
		args = parser.parse_args()

		if args.pem is not None:
		   pem = args.pem
		else:
			pem = raw_input('Path to pem key: ')

		if args.region is not None:
			aws_region = args.region
		else:
			aws_region = raw_input('AWS Region where your servers live: ')

		if args.inventory is not None:
			inventory_file = args.inventory
		else:
			inventory_file = raw_input('Enter a name for your inventory file: ')

		if args.profile is not None:
			profile = args.profile
		else:
			profile = 'default'

		print('Creating your inventory file: %s' % inventory_file)
		self.find(pem, aws_region, profile)
		self.create(inventory_file)

	def find(self, pem, aws_region, profile):
		session = boto3.Session(profile_name=profile, region_name=aws_region)
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
		# Decrypt password by aws-id and pem key
		for reservations in instances.get('Reservations'):
			for instance in reservations.get('Instances'):
				instance_id = instance.get('InstanceId')
				private_dns_name = instance.get('PrivateDnsName')
				environment = 'null'
				role = 'null'
				name = 'null'
				tmp_environment = {}

				for tag in instance.get('Tags'):
					if tag is None: 
						break
					elif tag.get('Key') == 'environment':
						environment = tag.get('Value')
						tmp_environment['env'] = environment
						passwd = None
					elif tag.get('Key') == 'role':
						role = tag.get('Value')
						tmp_environment['role'] = role

					elif tag.get('Key') == 'Name':
						name = tag.get('Value')



				if instance.get('KeyName') == 'ci-validation':
					get_pw_cmd = 'aws ec2 get-password-data --instance-id %s --priv-launch-key %s' % (instance_id, pem)
					get_pw = subprocess.Popen(get_pw_cmd, stdout=PIPE, stderr=PIPE, shell=True)
					out, err = get_pw.communicate()
					if err:
						print("Error Decrypting Keys %s " % err)
						sys.exit(1)

					pw = json.loads(out)

					if passwd is None:
						passwd = pw.get('PasswordData')
				else:
					 passwd = 'null'

				if tmp_environment not in environments:
					environments.append(tmp_environment)

				hosts.append({'env': environment, 'role': role, 'name':name, 'private_dns_name': private_dns_name, 'win_password': passwd})

	def create(self, file):
		inventory = open('./inventory/' + file, 'w')
		#Creating inventory file
	 	inventory.write ('[windows:children]\n')
		
		# Generate List of all Environments
		list_of_envs = []
	 	for i, environment in enumerate(environments):

	 		if environment['env'] not in list_of_envs:
	 			inventory.write('%s\n' % environment['env'])
	 			list_of_envs.append(environment['env'])

	 		if i == len(environments) -1:
	 			inventory.write('\n')

	 	# Generate all the roles for each environment
	 	list_of_roles = []
	 	for i, env in enumerate(list_of_envs):
	 		curr_env = list(filter(lambda x: x['env'] == env, environments))

	 		inventory.write('[%s:children]\n' % env)

	 		for length, e in enumerate(curr_env):
	 			inventory.write('%s-%s\n' % (e['env'], e['role']))
	 			list_of_roles.append('%s-%s' % (e['env'], e['role']))

	 			if length == len(curr_env) -1:
	 				inventory.write('\n')
		
		# Generate the list of hosts per role of each environment
	 	for i, environment in enumerate(environments):
	 		curr_env = list(filter(lambda x: x['env'] == environment['env'], hosts))
	 		servers = list(filter(lambda x: x['role'] == environment['role'], curr_env))

	 		inventory.write('[%s-%s]\n' % (environment['env'], environment['role']))

	 		for length, server in enumerate(servers):
	 			inventory.write ('%s ansible_host=%s ansible_user=Administrator ansible_password="%s" ansible_port=5986 ansible_connection=winrm\n' % (server['name'], server['private_dns_name'], server['win_password']))

	 			if length == len(servers) -1:
	 				inventory.write('\n')

	 	inventory.close()

Generator()