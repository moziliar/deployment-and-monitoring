from email.mime import base
from enum import Enum
import os

import yaml
from typing import Dict, Set

import ssh
from report import report
import basedata

class MachineList(basedata.Data):
    def __init__(self):
        super().__init__()
        self.machines: Dict[str, Machine] = {}

    def load_yaml(self, filepath):
        super().load_yaml(filepath)

        print('machines read; try setting up ssh-copy-id on machines')
        # for machine in self.machines.keys():
            # os.system(f'ssh-copy-id {os.getenv("SSH_USER")}@{machine}')
    
    def load_object(self, name, attr):
        self.machines[name] = Machine.from_yaml(name, attr)

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

    def get_data(self):
        return self.machines


class MachineStatus(Enum):
    UNKNOWN = 'unknown'
    READY = 'ready'
    UNREACHABLE = 'unreachable'


class MachineCannotSyncException(Exception):
    pass


class Machine(basedata.DataEntity):
    dynamic_fields: Set[str] = {'status'}
    static_fields: Set[str] = {
        'name',
        'os',
        'kernel',
        'version',
        'role',
    }

    def __str__(self) -> str:
        return f'nodename: {self.name}, \
                status: {self.status=}, \
                os: {self.os}, \
                version: {self.version}, \
                role: {self.role}'

    def __init__(self, name):
        super().__init__(name)
        self.status = MachineStatus.UNKNOWN
        self.os = ''
        self.kernel = ''
        self.version = ''
        self.role = ''

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

        self.os = os
        self.kernel = kernel
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
        if self.role:
            ret['role'] = self.role
        return ret


machine_list = MachineList()
