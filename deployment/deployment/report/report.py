import os
from collections import defaultdict

import yaml


class Report(object):
    def __init__(self):
        self.diff = defaultdict(list)

    def check_and_report_diff(
            self,
            entry_type: str,
            nodename: str,
            item_name: str,
            want: str, got: str
    ):
        if want == '' or want == got:
            # either not want anything or no diff, assume to not report
            return
        self.add_diff(entry_type, f'{nodename}: wanted {item_name} "{want}", got {got}')

    def add_diff(self, entry_type: str, entry: str):
        self.diff[entry_type].append(entry)

    def save_to_yaml(self):
        report_path = os.path.join(os.getenv("PWD"), 'resources/report.yaml')
        print(f'generate report at {report_path}')
        with open(report_path, 'w') as f:
            report_dict = {'diff': dict(self.diff)}
            yaml.dump(report_dict, f)


report = Report()
