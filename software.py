from collections import defaultdict

import yaml

import ssh


class SoftwareList(object):
    def __init__(self):
        self.softwares = {}
        self.filepath = ''

    def load_yaml(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r') as f:
            _software_list = yaml.safe_load(f)
            if not software_list:
                return
            for name, attr in _software_list.items():
                self.softwares[name] = Software.from_yaml(name, attr)

    def inspect_all_on_machines(self, machines):
        for software in self.softwares.values():
            software.inspect_on_machines(machines)
        self.write_back()

    def write_back(self):
        with open(self.filepath, 'w') as f:
            software_dict = {}
            for software in self.softwares.values():
                software_dict[software.name] = software.to_dict()
            yaml.dump(software_dict, f)


class Software(object):
    def __init__(self, name, version=''):
        self.name = name
        self.version = version
        self.machine_to_version = {}

    @classmethod
    def from_yaml(cls, key, val):
        s = cls(key)
        if type(val) != dict:
            return s
        for k, v in val.items():
            s.__setattr__(k, v)
        return s

    def inspect_on_machines(self, machines):
        version_count = defaultdict(list)
        for machine in machines:
            output, success = ssh.client.exec_on_machine(machine, f'{self.name} --version | grep {self.name}')
            if not success:
                self.machine_to_version[machine] = 'unknown'
                return
            version = output.stdout.strip()
            self.machine_to_version[machine] = version
            version_count[version].append(machine)

        to_remove = []
        version_to_display = ''
        for version, machines in version_count.items():
            if len(machines) > len(to_remove):
                to_remove = machines
                version_to_display = version
        self.version = version_to_display

    def to_dict(self):
        ret = {'version': self.version}
        mismatch= {k: v for k, v in self.machine_to_version.items() if v != self.version}
        if mismatch:
            ret['mismatch'] = mismatch
        return ret


software_list = SoftwareList()
