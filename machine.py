from enum import Enum

import yaml

import ssh


class MachineList(object):
    def __init__(self):
        self.filepath = ''
        self.machines = {}

    def load_yaml(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r') as f:
            machines = yaml.safe_load(f)
            for name, attr in machines.items():
                self.machines[name] = Machine.from_yaml(name, attr)

    def inspect_all(self):
        for machine in self.machines.values():
            machine.inspect()
        self.write_back()

    def write_back(self):
        with open(self.filepath, 'w') as f:
            machine_dict = {}
            for machine in self.machines.values():
                machine_dict[machine.name] = machine.to_dict()
            yaml.dump(machine_dict, f)


class MachineStatus(Enum):
    UNKNOWN = 'unknown'
    READY = 'ready'
    UNREACHABLE = 'unreachable'


class Machine(object):
    dynamic_variables = {'status'}

    def __str__(self):
        return f'nodename: {self.name}, status: {self.status=}, os: {self.os}, version: {self.version}'

    def __init__(self, name):
        self.name = name
        self.status = MachineStatus.UNKNOWN
        self.os = ''
        self.kernel = ''
        self.version = ''

    @classmethod
    def from_yaml(cls, key, val):
        m = cls(key)
        if type(val) != dict:
            return m
        for k, v in val.items():
            if k in cls.dynamic_variables:
                continue
            m.__setattr__(k, v)
        return m

    def inspect(self):
        output, success = ssh.client.exec_on_machine(self.name, 'uname -s; uname -r; lsb_release -ds')
        if not success:
            self.status = MachineStatus.UNREACHABLE
            return
        parsed = output.stdout.split('\n')
        if len(parsed) < 3:
            # TODO: handle failure
            return
        self.os = parsed[0]
        self.kernel = parsed[1]
        self.version = parsed[2]
        self.status = MachineStatus.READY

    def to_dict(self):
        ret = {
            'status': self.status.name
        }
        if self.os:
            ret['os'] = self.os
        if self.kernel:
            ret['kernel'] = self.kernel
        if self.version:
            ret['version'] = self.version
        return ret


machine_list = MachineList()
