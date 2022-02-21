import os

import click
from dotenv import load_dotenv
import yaml

from machine import MachineList, machine_list, MachineCannotSyncException
from report import report
from software import SoftwareList, software_list
from usergroup import UserList, user_list

# @click.command()
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--name', prompt='Your name',
#               help='The person to greet.')
# def hello(count, name):
#     """Simple program that greets NAME for a total of COUNT times."""
#     for x in range(count):
#         click.echo(f"Hello {name}!")
load_dotenv()


@click.group()
def cli():
    pass


@click.command()
def init():
    machine_list.inspect_all()
    software_list.inspect_all_on_machines(machine_list.machines.keys())
    user_list.inspect_all_on_machines(machine_list.machines.keys())

    report.save_to_yaml()


@click.command()
def sync():
    try:
        machine_list.introspect()
    except MachineCannotSyncException:
        print('machines not ready to sync')
        return

    user_sync_file = user_list.diff_all_on_machines(machine_list.machines.keys())
    software_sync_file = software_list.diff_all_on_machines(machine_list.machines.keys())

    with open('user_play.yaml', 'w') as f:
        yaml.dump(user_sync_file, f)
    with open('software_play.yaml', 'w') as f:
        yaml.dump(software_sync_file, f)

    report.save_to_yaml()


if __name__ == '__main__':
    machine_list_data = MachineList.open_yaml('machine-list.yaml')
    software_list_data = SoftwareList.open_yaml('software-list.yaml')
    user_list_data = UserList.open_yaml('user-list.yaml')
    machine_list.load_yaml(machine_list_data)
    software_list.load_yaml(software_list_data)
    user_list.load_yaml(user_list_data)

    cli.add_command(init)
    cli.add_command(sync)
    cli()
