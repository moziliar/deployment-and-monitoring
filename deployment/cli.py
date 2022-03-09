import os

import click
from dotenv import load_dotenv

from machine import MachineList, machine_list, MachineCannotSyncException
from report import report
from software import SoftwareList, software_list
from usergroup import UserList, user_list

load_dotenv()


def setup():
    import rpyc
    c = rpyc.connect(os.environ["DEPLOYMENT_SERVER"], 18861, config = {"allow_public_attrs" : True})
    return c


def load_yaml():
    machine_list_data = MachineList.open_yaml('machine-list.yaml')
    software_list_data = SoftwareList.open_yaml('software-list.yaml')
    user_list_data = UserList.open_yaml('user-list.yaml')

    return machine_list_data, software_list_data, user_list_data


@click.group()
def cli():
    pass


@click.command()
@click.option('--force', default=False, help='Force init machine-list.yaml, software-list.yaml, and user-list.yaml')
def init(force):
    """
    Init the local state files from the remote machines.
    """
    machine_list_data, software_list_data, user_list_data = load_yaml()

    # RPC call to centralized server
    server = setup()
    server.root.init(machine_list_data, software_list_data, user_list_data)


@click.command()
@click.option('--force', default=False, help='Force sync to machines without prompt')
def sync(force):
    """
    Sync the local state files to the remote machines.
    """
    machine_list_data, software_list_data, user_list_data = load_yaml()

    # RPC call to centralized server
    server = setup()
    server.root.sync(machine_list_data, software_list_data, user_list_data)


if __name__ == '__main__':
    cli.add_command(init)
    cli.add_command(sync)
    cli()
