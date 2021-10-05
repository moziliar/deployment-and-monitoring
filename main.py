import os

import click
from dotenv import load_dotenv

from machine import machine_list
from software import software_list
from usergroup import user_list

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


if __name__ == '__main__':
    machine_list.load_yaml('machine-list.yaml')
    software_list.load_yaml('software-list.yaml')
    user_list.load_yaml('user-list.yaml')

    cli.add_command(init)
    cli()
