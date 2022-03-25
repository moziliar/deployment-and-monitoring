import subprocess


def run_ansible_at(path):
    sync_user_proc = subprocess.Popen([
        'ansible-playbook',
        path,
        '-f', '20',
        '--become', '--vault-password-file=vault.txt'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return sync_user_proc.communicate()
