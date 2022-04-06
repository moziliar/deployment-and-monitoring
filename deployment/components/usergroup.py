import os
from collections import defaultdict

from components import templates
from components.basedata import Data, DataEntity
from conn import ssh


class UserList(Data):
    def __init__(self):
        super().__init__()
        self.user_groups = {}

    def load_object(self, name, attr):
        self.user_groups[name] = UserGroup.from_yaml(name, attr)

    def get_data(self):
        return self.user_groups

    def inspect_all_on_machines(self, machines):
        print('inspecting users on machines')
        for user_group in self.user_groups.values():
            print(f'inspecting usergroup {user_group.name}')
            user_group.inspect_on_machines(machines)

    def diff_all_on_machines(self, machines):
        print('check difference in software on machines')
        users_to_add, users_to_remove = defaultdict(list), defaultdict(list)
        for user_group in self.user_groups.values():
            print(f'inspecting user_group {user_group.name}')
            users_to_add_for_group, users_to_remove_for_group = user_group.diff_on_machines(machines)
            for user, machines in users_to_add_for_group.items():
                users_to_add[user] += machines
            for user, machines in users_to_remove_for_group.items():
                users_to_remove[user] += machines
        return templates.get_sync_user_play(
            machines,
            os.getenv('SSH_USER'),
            users_to_add,
            users_to_remove,
        )


class UserGroup(DataEntity):
    def __init__(self, name):
        super().__init__(name)
        self.users = {}
        self.remote_user_to_machines = defaultdict(list)
        self.machine_set = set()

    @classmethod
    def from_yaml(cls, key, val):
        ug = super().from_yaml(key, val)
        if ug.users is None:
            ug.users = {}
        ug.users = {name: User(name=name, group=ug.name) for name in ug.users}
        return ug

    def to_dict(self):
        ret = {'users': {}}
        for user, machines in self.remote_user_to_machines.items():
            missing_on_machines = self.machine_set - set(machines)
            if len(missing_on_machines) != 0:
                ret['users'][user] = dict({'missing on': list(missing_on_machines)})
            else:
                ret['users'][user] = None
        return ret

    def inspect_on_machines(self, machines):
        self.machine_set = set(machines)
        for machine in machines:
            output, success = ssh.client.exec_on_machine(machine,
                                                         f"id=$(getent group {self.name} | cut -d: -f3); echo $id | awk -v id=$id -F: '{{if ($4 == id) {{print $0}}}}' /etc/passwd")
            if not success:
                print(f'exec on {machine} failed')
                continue
            users = output.stdout.split('\n')
            for user_str in filter(lambda u: u.strip() != '', users):
                name, _, uid, gid, _, homedir, shell = user_str.split(':')
                self.remote_user_to_machines[name].append(machine)

    def diff_on_machines(self, machines):
        users_to_add = {}
        users_to_remove = {}

        self.inspect_on_machines(machines)

        # Inspect missing users
        for user, _ in self.users.items():
            if user not in self.remote_user_to_machines:
                users_to_add[self.users[user]] = machines
                continue
            diff = set(machines) - set(self.remote_user_to_machines.get(user))
            if diff:
                users_to_add[self.users[user]] = diff

        # Inspect extra users
        for user, remote_machines in self.remote_user_to_machines.items():
            if user not in self.remote_user_to_machines:
                # Add user
                users_to_remove[self.users[user]] = remote_machines
                continue
            diff = set(remote_machines) - set(machines)
            if diff:
                users_to_remove[self.users[user]] = diff

        return users_to_add, users_to_remove


class User(object):
    def __init__(self, name, group, uid=0, gid=0, homedir=None, shell=None):
        self.name = name
        self.group = group
        self.uid = uid
        self.gid = gid
        self.homedir = homedir
        self.shell = shell


user_list = UserList()
