import subprocess
import os

import click
from dotenv import load_dotenv

from components.machine import MachineList
from components.software import SoftwareList
from components.usergroup import UserList

load_dotenv()

token = ''


def setup():
    # Obtain munge token
    global token
    token_proc = subprocess.run(['munge', '-n'], capture_output=True)
    token = token_proc.stdout

    import rpyc
    c = rpyc.connect(os.environ["DEPLOYMENT_SERVER"], 18861, config = {"allow_public_attrs" : True})
    return c


def load_yaml():
    machine_list_data = MachineList.open_yaml('resources/machine-list.yaml')
    software_list_data = SoftwareList.open_yaml('resources/software-list.yaml')
    user_list_data = UserList.open_yaml('resources/user-list.yaml')

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
    server.root.init(token, machine_list_data, software_list_data, user_list_data)


@click.command()
@click.option('--force', default=False, help='Force sync to machines without prompt')
def sync(force):
    """
    Sync the local state files to the remote machines.
    """
    machine_list_data, software_list_data, user_list_data = load_yaml()

    # RPC call to centralized server
    server = setup()
    try:
        server.root.sync(token, machine_list_data, software_list_data, user_list_data)
    except Exception as err:
        print(err)


if __name__ == '__main__':
    cli.add_command(init)
    cli.add_command(sync)
    cli()
