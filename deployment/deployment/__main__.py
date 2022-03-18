import rpyc
from dotenv import load_dotenv

from components.machine import machine_list, MachineCannotSyncException
from components.software import software_list
from components.usergroup import user_list
from report.report import report
from utils.token import verify_user
from utils.run import dump_to_playbook_at, run_ansible_at

load_dotenv()


def setup(machine_list_data, software_list_data, user_list_data):
    print("setting", machine_list_data)
    machine_list.load_yaml(dict(machine_list_data))
    print("set up machine")
    software_list.load_yaml(dict(software_list_data))
    print("set up soft")
    user_list.load_yaml(dict(user_list_data))
    print("set up user")


class DeploymentService(rpyc.Service):
    def __init__(self):
        self.conn = None

    def on_connect(self, conn):
        self.conn = conn

    def on_disconnect(self, conn):
        pass

    def exposed_init(self, token, machine_list_data, software_list_data, user_list_data):
        setup(machine_list_data, software_list_data, user_list_data)
        machine_list.inspect_all()
        software_list.inspect_all_on_machines(machine_list.machines.keys())
        user_list.inspect_all_on_machines(machine_list.machines.keys())

        # Write back at client side
        self.conn.root.machine_list.write_back()
        self.conn.root.software_list.write_back()
        self.conn.root.user_list.write_back()

        report.save_to_yaml()

    def exposed_sync(self, token, machine_list_data, software_list_data, user_list_data):
        if not verify_user(token):
            return
        verify_user(token)
        setup(machine_list_data, software_list_data, user_list_data)
        print('serving')

        try:
            machine_list.introspect()
        except MachineCannotSyncException:
            print('machines not ready to sync')
            return

        user_sync_file = user_list.diff_all_on_machines(machine_list.machines.keys())
        software_sync_file = software_list.diff_all_on_machines(machine_list.machines.keys())

        dump_to_playbook_at('/tmp/ansible/user_play.yaml', user_sync_file)
        dump_to_playbook_at('/tmp/ansible/software_play.yaml', software_sync_file)

        stdout, stderr = run_ansible_at('/tmp/ansible/user_play.yaml')
        print(str(stdout))
        stdout, stderr = run_ansible_at('/tmp/ansible/software_play.yaml')
        print(str(stdout))

        report.save_to_yaml()


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(DeploymentService, port=18861, protocol_config = {"allow_public_attrs" : True})
    t.start()
