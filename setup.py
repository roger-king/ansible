#!/usr/bin/env python

"""
	I'm a fan of automation.
	Let's go ahead setup your Environment!
	Just Run the script, I promise it will work... maybe, don't call if it doesn't.
"""

import os
import argparse
import sys
import stat

class Setup(object):
	def __init__(self):
		self.executable()
		self.add_pem()
		self.create_py_env()
		self.run_virtualenv()
		self.install_requirements()

	def cli(self, cmd):
		from subprocess import Popen

		cli = Popen(cmd, shell=True)
		cli.wait()
		return cli.returncode

	def cmdCodeIsOk(self, code):
		if code == 0:
			return True
		else:
			return False

	def executable(self):
		st = os.stat('./inventory/ec2.py')
		os.chmod('./inventory/ec2.py', st.st_mode | stat.S_IEXEC)

	def add_pem(self):
		key_path = raw_input("Path to your pem-key: ")
		cmd = 'ssh-add ' + key_path

		code = self.cli(cmd)

		if not self.cmdCodeIsOk(code):
			sys.exit(1)
			print('Failed to add pem key. Please check your path')

	def create_py_env(self):
		print('Create virtual env')
		virtualenv = 'virtualenv env'
		ve = self.cli(virtualenv)
		if not self.cmdCodeIsOk(ve):
			print('Im going to assume virtualenv is not installed.')
			pip_install = 'pip install virtualenv'
			print('Installing pip for you.')
			pip = self.cli(pip_install)
			if not self.cmdCodeIsOk:
				sys.exit(1)
				print("okay I can't do everything for you... Install pip")
			else:
				print('Okay getting closer. lets try and install virtualenv again')
		else:
			print('virtual env created.')
			return

		ve = self.cli(virtualenv)
		if not self.cmdCodeIsOk(ve):
			sys.exit(1)
			print('okay you are having other issues... i dont know whats wrong.')

	def run_virtualenv(self):
		activate = 'source env/bin/activate'
		code = self.cli(activate)
		if not self.cmdCodeIsOk(code):
			print('Check your virtualenv has been created. Its called env')
			sys.exit(1)
		else:
			print('Virtual env has been activated.')


	def install_requirements(self):
		install = 'pip install -r requirements.txt'
		code = self.cli(install)
		if not self.cmdCodeIsOk(code):
			print('could not install requirements. Maybe check your internet connection.')
			print('If you made it this far. Pip SHOULD be installed.')
			sys.exit(1)

		print('Requirements installed')
		print('One last step: Please run source env/bin/activate')

Setup()