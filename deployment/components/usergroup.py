from collections import defaultdict

import templates
from basedata import Data, DataEntity
from deployment.conn import ssh


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
        users_to_add, users_to_remove = [], []
        for user_group in self.user_groups.values():
            print(f'inspecting user_group {user_group.name}')
            _users_to_add, _users_to_remove = user_group.diff_on_machines(machines)
            users_to_add += [User(name=name, group=user_group.name) for name in _users_to_add.keys()]
            users_to_remove += [User(name=name, group=user_group.name) for name in _users_to_remove.keys()]
        return templates.get_sync_user_play(
            'labmachines',
            'mzr',
            users_to_add,
            users_to_remove,
        )


class UserGroup(DataEntity):
    def __init__(self, name):
        super().__init__(name)
        self.users = {}
        self.user_to_machines = defaultdict(list)
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
        for user, machines in self.user_to_machines.items():
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
                self.user_to_machines[name].append(machine)

    def diff_on_machines(self, machines):
        users_to_add = {}
        users_to_remove = {}
        remote_user_to_machines = defaultdict(list)

        self.inspect_on_machines(machines)

        # Inspect existing users on the machines
        for machine in machines:
            output, success = ssh.client.exec_on_machine(machine,
                                                         f"id=$(getent group {self.name} | cut -d: -f3); echo $id | awk -v id=$id -F: '{{if ($4 == id) {{print $0}}}}' /etc/passwd")
            if not success:
                continue
            users = output.stdout.split('\n')
            for user_str in users:
                if user_str.strip() == '':
                    continue
                name, _, uid, gid, _, homedir, shell = user_str.split(':')
                remote_user_to_machines[name].append(machine)

        # Inspect missing users
        for user, _ in self.user_to_machines.items():
            if user not in remote_user_to_machines:
                users_to_add[user] = machines
                continue
            diff = set(machines) - set(remote_user_to_machines.get(user))
            if len(diff) > 0:
                users_to_add[user] = diff

        # Inspect extra users
        for user, remote_machines in remote_user_to_machines.items():
            if user not in self.user_to_machines:
                # Add user
                users_to_remove[user] = remote_machines
                continue
            diff = set(remote_machines) - set(machines)
            if len(diff) > 0:
                users_to_remove[user] = diff

        return users_to_add, users_to_remove

    def sync_users(self, users_to_add, users_to_remove):
        # Generate ansible playbook to perform operation
        print(templates.get_sync_user_play(users_to_add, users_to_remove))


class User(object):
    def __init__(self, name, group, uid=0, gid=0, homedir=None, shell=None):
        self.name = name
        self.group = group
        self.uid = uid
        self.gid = gid
        self.homedir = homedir
        self.shell = shell


user_list = UserList()
