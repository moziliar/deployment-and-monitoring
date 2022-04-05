import subprocess


def run_ansible_at(path):
    return subprocess.run([
        'ansible-playbook',
        path,
        '-f', '20',
        '--become', '--vault-password-file=vault.txt'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
