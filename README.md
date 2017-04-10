## About:

My take on my ideal workflow of an ansible repository.
In a nutshell, the repository workflow is playbooks call the roles and the roles are the main logic work force.
Creation of modular and reusable roles is the key to success in this repository.

* This project seed is geared towards AWS dynamic inventory.
* Update to come to be more dynamic.

## Requirements:

1. pip - this is the package manager that we will be using. Please be sure you have it installed.

- How to install: use `brew install pip`

*I try to automate the setup process as much as I can*

## Setup:

1. Set your pem key path in ansible.cfg
2. Set the default or desired user for the servers.

To setup your environment run the setup script and when it runs successfully run virtualenv to enter your virtualenv.

```
	chmod +x setup.py
	./setup.py
	source env/bin/activate
	pip install -r requirements.txt
	ansible-galaxy install -p roles/external -r roles.txt
```

* When running commands, if you are encountering an error where it cannot find a role.
*By default, ansible looks in /etc/ansible for the .cfg file. set your ANSIBLE_CONFIG to point to the this .cfg (./ansible.cfg)

## Use Cases:

#### Windows:

We have a custom python file that we use to setup the inventory file for windows management.

```
chmod +x scripts/aws/win_inventory_generator.py
./scripts/aws/win_inventory_generator.py --pem ~/.ssh/your-pem.pem --region us-east-1 --inventory win-inventory --profile default
```
This will create a file named "win-inventory" in the "inventory" folder.


##### Example:

Provision a windows server.
```
ansible-playbook -i ./inventory/win-inventory playbooks/windows.yml -e "target={target-server}" --tags "provision"
```

The key here is the tags flag. 

What this allows us to do is bunch up all our roles/tasks in a single playbook and call those roles/tasks.

Here we are only calling the roles/tasks that are needed to provision the server. 

If we wanted to deploy the application instead of "provision", we would call "deploy". 

Same would apply if we wanted to just call a single role/task, like restarting a service.

#### Linux

By default, Ansible will look into the inventory folder and find the ec2.py file and use that as our dynamic inventory file.

If you want to specify individual environments, instances, and or by role, you would have to pass into the playbooks an extra variable (-e) "target" and assign the server(s) you'd like to run your playbook against. 

For AWS dynamic inventory file, to find servers by tags you assign the "target" variable tag_Key_Value (i.e: tag_environment_test)

*Keep Note that ansible parses - and replaces with _. i.e: test-server as test_server.
