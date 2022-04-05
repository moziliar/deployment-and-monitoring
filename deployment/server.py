import rpyc
from dotenv import load_dotenv

from components.machine import machine_list, MachineCannotSyncException
from components.software import software_list
from components.usergroup import user_list
from report.report import report
from utils.file import dump_to_playbook_at
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
        machine_list.inspect_all()
        software_list.inspect_all_on_machines(machine_list.machines.keys())
        user_list.inspect_all_on_machines(machine_list.machines.keys())

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

        user_sync_file = user_list.diff_all_on_machines(machine_list.machines.keys())
        software_sync_file = software_list.diff_all_on_machines(machine_list.machines.keys())

        dump_to_playbook_at('/tmp/ansible/user_play.yaml', user_sync_file)
        dump_to_playbook_at('/tmp/ansible/software_play.yaml', software_sync_file)

        stdout, stderr = run_ansible_at('/tmp/ansible/user_play.yaml')
        self.conn.root.client_print(stdout.encode('utf-8'))
        stdout, stderr = run_ansible_at('/tmp/ansible/software_play.yaml')
        self.conn.root.client_print(stdout.encode('utf-8'))

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
