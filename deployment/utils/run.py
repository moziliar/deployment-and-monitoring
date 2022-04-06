import os
import subprocess


def run_ansible_at(path, playbook):
    return subprocess.run([
        'ansible-playbook',
        os.path.join(path, playbook),
        '-i', os.path.join(path, 'hosts'),
        '-f', '20',
        '--become', '--vault-password-file=vault.txt'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
