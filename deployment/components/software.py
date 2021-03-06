import os
from collections import defaultdict

from components import templates
from components.basedata import Data, DataEntity
from conn import ssh


class SoftwareList(Data):
    def __init__(self):
        super().__init__()
        self.softwares = {}

    def load_object(self, name, attr):
        self.softwares[name] = Software.from_yaml(name, attr)

    def get_data(self):
        return self.softwares

    def inspect_all_on_machines(self, machines):
        print('inspecting software on machines')
        for software in self.softwares.values():
            print(f'inspecting software {software.name}')
            software.inspect_on_machines(machines)

    def diff_all_on_machines(self, machines):
        print('check difference in software on machines')
        for software in self.softwares.values():
            print(f'inspecting software {software.name}')
            software.inspect_on_machines(machines)
            print(software)
        return [templates.get_sync_software_play(
            'labmachines', 
            os.getenv('SSH_USER'),
            list(self.softwares.values())
        )]


class Software(DataEntity):
    def __init__(self, name, version='latest', package=''):
        super().__init__(name)
        self.version = version
        self.package = package
        self.machine_to_version = {}
        self.machine_to_package = {}

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
            if not ret:
                self.machine_to_version[machine] = 'unknown'
                continue
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
