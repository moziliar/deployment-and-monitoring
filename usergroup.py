from collections import defaultdict

import yaml

import ssh


class UserList(object):
    def __init__(self):
        self.user_groups = {}
        self.filepath = ''

    def load_yaml(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r') as f:
            _user_group_list = yaml.safe_load(f)
            if not _user_group_list:
                return
            for name, attr in _user_group_list.items():
                self.user_groups[name] = UserGroup.from_yaml(name, attr)

    def inspect_all_on_machines(self, machines):
        for user_group in self.user_groups.values():
            user_group.inspect_on_machines(machines)
        self.write_back()

    def write_back(self):
        with open(self.filepath, 'w') as f:
            user_group_dict = {}
            for user_group in self.user_groups.values():
                user_group_dict[user_group.name] = user_group.to_dict()
            yaml.dump(user_group_dict, f)


class UserGroup(object):
    def __init__(self, name):
        self.name = name
        self.user_to_machines = defaultdict(list)

    @classmethod
    def from_yaml(cls, key, val):
        u = cls(key)
        if type(val) != dict:
            return u
        for k, v in val.items():
            u.__setattr__(k, v)
        return u

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
