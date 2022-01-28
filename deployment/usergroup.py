from collections import defaultdict

import yaml

import ssh

import basedata

class UserList(basedata.Data):
    def __init__(self):
        super().__init__()
        self.user_groups = {}

    def load_object(self, name, attr):
        self.user_groups[name] = UserGroup.from_yaml(name, attr)

    def inspect_all_on_machines(self, machines):
        print('inspecting users on machines')
        for user_group in self.user_groups.values():
            print(f'inspecting usergroup {user_group.name}')
            user_group.inspect_on_machines(machines)
        self.write_back()

    def get_data(self):
        return self.user_groups


class UserGroup(basedata.DataEntity):
    def __init__(self, name):
        super().__init__(name)
        self.user_to_machines = defaultdict(list)

    def inspect_on_machines(self, machines):
        for machine in machines:
            output, success = ssh.client.exec_on_machine(machine, f"id=$(getent group {self.name} | cut -d: -f3); echo $id | awk -v id=$id -F: '{{if ($4 == id) {{print $0}}}}' /etc/passwd")
            if not success:
                continue
            users = output.stdout.split('\n')
            for user_str in users:
                if user_str.strip() == '':
                    continue
                name, _, uid, gid, _, homedir, shell = user_str.split(':')
                self.user_to_machines[name].append(machine)

    def to_dict(self):
        ret = {'users': list(self.user_to_machines.keys())}
        return ret


class User(object):
    def __init__(self, name, uid, gid, homedir=None, shell=None):
        self.name = name
        self.uid = uid
        self.gid = gid
        self.homedir = homedir
        self.shell = shell


user_list = UserList()
