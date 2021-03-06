import os
import time

import rpyc
from dotenv import load_dotenv

from components.machine import machine_list, MachineCannotSyncException
from components.software import software_list
from components.usergroup import user_list
from report.report import report
from utils.file import dump_to_playbook_at, generate_ini_file_at
from utils.token import verify_user
from utils.run import run_ansible_at

load_dotenv()


def setup(machine_list_data, software_list_data, user_list_data):
    print("setting", machine_list_data)
    machine_list.load_yaml(machine_list_data)
    print("set up machine")
    software_list.load_yaml(software_list_data)
    print("set up soft")
    user_list.load_yaml(user_list_data)
    print("set up user")


class DeploymentService(rpyc.Service):
    def __init__(self):
        self.conn = None

    def on_connect(self, conn):
        if self.conn is None:
            self.conn = conn
        else:
            raise Exception('someone is provisioning the machines')

    def on_disconnect(self, conn):
        self.conn = None

    def exposed_init(self, token, machine_list_data, software_list_data, user_list_data):
        setup(
            rpyc.classic.obtain(machine_list_data),
            rpyc.classic.obtain(software_list_data),
            rpyc.classic.obtain(user_list_data)
        )
        self.conn.root.client_print('inspecting machine information')
        machine_list.inspect_all()
        self.conn.root.client_print('inspecting software on all machines')
        software_list.inspect_all_on_machines(machine_list.machines.keys())
        self.conn.root.client_print('inspecting users on all machines')
        user_list.inspect_all_on_machines(machine_list.machines.keys())

        self.conn.root.client_print('save to client resource state file')
        # Write back at client side
        self.conn.root.save_yaml(
            machine_list.get_data(),
            software_list.get_data(),
            user_list.get_data()
        )

    def exposed_sync(self, token, machine_list_data, software_list_data, user_list_data):
        try:
            verify_user(token)
        except Exception as e:
            self.conn.root.client_print(e)
            raise e

        setup(
            rpyc.classic.obtain(machine_list_data),
            rpyc.classic.obtain(software_list_data),
            rpyc.classic.obtain(user_list_data)
        )

        try:
            self.conn.root.client_print('introspecting machine information')
            machine_list.introspect()
        except MachineCannotSyncException:
            self.conn.root.client_print('machines not ready to sync')
            return

        playbook_dir = '/tmp/ansible'
        user_play_name = 'user_play.yaml'
        software_play_name = 'software_play.yaml'

        self.conn.root.client_print('diff users on all machines')
        user_sync_file, host_map = user_list.diff_all_on_machines(machine_list.machines.keys())
        self.conn.root.client_print('diff software on all machines')
        software_sync_file = software_list.diff_all_on_machines(machine_list.machines.keys())

        self.conn.root.client_print('generate ansible playbooks')
        generate_ini_file_at(host_map, os.path.join(playbook_dir, 'hosts'))

        dump_to_playbook_at(os.path.join(playbook_dir, user_play_name), user_sync_file)
        dump_to_playbook_at(os.path.join(playbook_dir, software_play_name), software_sync_file)

        self.conn.root.client_print('run ansible playbooks')
        proc = run_ansible_at(playbook_dir, user_play_name)
        time.sleep(1)
        while proc.poll() is None:
            time.sleep(3)
            self.conn.root.client_print('ansible still running')
        self.conn.root.client_print(proc.stdout)

        proc = run_ansible_at(playbook_dir, software_play_name)
        time.sleep(1)
        while proc.poll() is None:
            time.sleep(3)
            self.conn.root.client_print('ansible still running')
        self.conn.root.client_print(proc.stdout)

        self.conn.root.client_print('save changes to report')
        report.save_to_yaml()


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    t = ThreadedServer(
        DeploymentService, port=18861,
        protocol_config={
            "allow_pickle": True,
            "allow_public_attrs": True
        }
    )
    t.start()
