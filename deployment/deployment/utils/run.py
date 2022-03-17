import subprocess
import yaml


def dump_to_playbook_at(path, data):
    with open(path, 'w') as f:
        yaml.dump([data], f)


def run_ansible_at(path):
    sync_user_proc = subprocess.Popen([
        'ansible-playbook',
        path,
        '-f', '20',
        '-i', 'ansible/hosts',
        '--become', '-K'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return sync_user_proc.communicate()
