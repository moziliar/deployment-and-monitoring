from enum import Enum
import os

import yaml
from typing import Dict, Set

import ssh
from report import report


class MachineList(object):
    def __init__(self):
        self.filepath: str = ''
        self.machines: Dict[str, Machine] = {}

    def load_yaml(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r') as f:
            machines = yaml.safe_load(f)
            for name, attr in machines.items():
                self.machines[name] = Machine.from_yaml(name, attr)

        print('machines read; try setting up ssh-copy-id on machines')
        for machine in self.machines.keys():
            os.system(f'ssh-copy-id {os.getenv("SSH_USER")}@{machine}')

    def inspect_all(self):
        print('inspecting machines')
        for machine in self.machines.values():
            print(f'inspecting machine {machine.name}')
            machine.inspect()
        self.write_back()

    def introspect(self):
        print('introspecting machines in files')
        for machine in self.machines.values():
            machine.introspect()
        print('machines ready to sync')

    def write_back(self):
        print('write back to machine-list')
        with open(self.filepath, 'w') as f:
            machine_dict = {}
            for machine in self.machines.values():
                machine_dict[machine.name] = machine.to_dict()
            yaml.dump(machine_dict, f)


class MachineStatus(Enum):
    UNKNOWN = 'unknown'
    READY = 'ready'
    UNREACHABLE = 'unreachable'


class MachineCannotSyncException(Exception):
    pass


class Machine(object):
    dynamic_fields: Set[str] = {'status'}
    static_fields: Set[str] = {
        'name',
        'os',
        'kernel',
        'version',
    }

    def __str__(self) -> str:
        return f'nodename: {self.name}, status: {self.status=}, os: {self.os}, version: {self.version}'

    def __init__(self, name):
        self.name = name
        self.status = MachineStatus.UNKNOWN
        self.os = ''
        self.kernel = ''
        self.version = ''

    @classmethod
    def from_yaml(cls, key, val) -> 'Machine':
        m = cls(key)
        if type(val) != dict:
            return m
        for k, v in val.items():
            if k in cls.dynamic_fields:
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
        [os, kernel, version, *_] = parsed

        report.check_and_report_diff('machine', self.name, 'os', self.os, os)
        self.os = os
        report.check_and_report_diff('machine', self.name, 'kernel', self.kernel, kernel)
        self.kernel = kernel
        report.check_and_report_diff('machine', self.name, 'version', self.version, version)
        self.version = version

        self.status = MachineStatus.READY

    '''
    :raises MachineCannotSyncException
    '''
    def introspect(self):
        if self.status is None or self.status != MachineStatus.READY:
            return
        for attr in Machine.static_fields:
            if self.__getattribute__(attr) == '':
                raise MachineCannotSyncException

    def to_dict(self) -> Dict[str, str]:
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
