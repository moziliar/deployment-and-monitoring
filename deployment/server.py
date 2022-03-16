import rpyc
import subprocess
import yaml

from machine import machine_list, MachineCannotSyncException
from report import report
from software import software_list
from usergroup import user_list

class DeploymentService(rpyc.Service):
    def on_connect(self, conn):
        self.conn = conn

    def on_disconnect(self, conn):
        pass

    def verify_user(self, token):
        verify_token_proc = subprocess.run(['unmunge'], input=token, capture_output=True)
        for line in verify_token_proc.stdout.decode('utf-8').splitlines():
            if line.startswith('GID') and 'sudo' in line:
                return
        raise Exception('non-sudo user')

    def setup(self, machine_list_data, software_list_data, user_list_data):
        print("setting", machine_list_data)
        machine_list.load_yaml(dict(machine_list_data))
        print("set up machine")
        software_list.load_yaml(dict(software_list_data))
        print("set up soft")
        user_list.load_yaml(dict(user_list_data))
        print("set up user")
    
    def exposed_init(self, token, machine_list_data, software_list_data, user_list_data):
        self.verify_user(token)
        self.setup(machine_list_data, software_list_data, user_list_data)
        machine_list.inspect_all()
        software_list.inspect_all_on_machines(machine_list.machines.keys())
        user_list.inspect_all_on_machines(machine_list.machines.keys())

        report.save_to_yaml()

    def exposed_sync(self, token, machine_list_data, software_list_data, user_list_data):
        if not self.verify_user(token):
            return
        self.verify_user(token)
        self.setup(machine_list_data, software_list_data, user_list_data)
        print('serving')

        try:
            machine_list.introspect()
        except MachineCannotSyncException:
            print('machines not ready to sync')
            return

        user_sync_file = user_list.diff_all_on_machines(machine_list.machines.keys())
        software_sync_file = software_list.diff_all_on_machines(machine_list.machines.keys())

        with open('ansible/user_play.yaml', 'w') as f:
            yaml.dump([user_sync_file], f)
        with open('ansible/software_play.yaml', 'w') as f:
            yaml.dump([software_sync_file], f)

        # Run playbooks
        sync_user_proc = subprocess.Popen([
            'ansible-playbook',
            'ansible/user_play.yaml',
            '-f', '20',
            '-i', 'ansible/hosts',
            '--become', '-K'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = sync_user_proc.communicate()
        print(str(stdout))

        # Run playbooks
        sync_software_proc = subprocess.Popen([
            'ansible-playbook',
            'ansible/software_play.yaml',
            '-f', '20',
            '-i', 'ansible/hosts',
            '--become', '-K'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = sync_software_proc.communicate()
        print(str(stdout))

        report.save_to_yaml()


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(DeploymentService, port=18861, protocol_config = {"allow_public_attrs" : True})
    t.start()