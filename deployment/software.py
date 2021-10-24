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
        print('inspecting software on machines')
        for software in self.softwares.values():
            print(f'inspecting software {software.name}')
            software.inspect_on_machines(machines)
        self.write_back()

    def diff_all_on_machines(self, machines):
        print('check difference in software on machines')
        for software in self.softwares.values():
            print(f'inspecting software {software.name}')
            software.inspect_on_machines(machines)
        self.write_back()

    def write_back(self):
        with open(self.filepath, 'w') as f:
            software_dict = {}
            for software in self.softwares.values():
                software_dict[software.name] = software.to_dict()
            yaml.dump(software_dict, f)


class Software(object):
    def __init__(self, name, version='', package=''):
        self.name = name
        self.version = version
        self.package = package
        self.machine_to_version = {}
        self.machine_to_package = {}

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
        package_count = defaultdict(list)
        for machine in machines:
            cmd = f"{self.name} --version | grep {self.name} | awk '{{print \"version:\" $0}}'; dpkg -S `which {self.name}` | awk -F: '{{print \"package:\" $1}}'"
            output, success = ssh.client.exec_on_machine(machine, cmd)
            if not success:
                self.machine_to_version[machine] = 'unknown'
                continue
            ret = output.stdout.strip()
            for line in ret.split('\n'):
                k, v = line.split(':')
                if k == 'version':
                    self.machine_to_version[machine] = v
                    version_count[v].append(machine)
                elif k == 'package':
                    self.machine_to_package[machine] = v
                    package_count[v].append(machine)

        count = 0
        version_to_display = ''
        for version, machines in version_count.items():
            if len(machines) > count:
                count = len(machines)
                version_to_display = version
        self.version = version_to_display

        count = 0
        package_to_display = ''
        for package, machines in package_count.items():
            if len(machines) > count:
                count = len(machines)
                package_to_display = package
        self.package = package_to_display

    def to_dict(self):
        ret = {'version': self.version}
        mismatch = {k: v for k, v in self.machine_to_version.items() if v != self.version}
        if mismatch:
            ret['mismatch'] = mismatch
        if self.package != '':
            ret['pacakge'] = self.package
        return ret


software_list = SoftwareList()
