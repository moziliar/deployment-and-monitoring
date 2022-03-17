import subprocess


def verify_user(token):
    # verify_user verifies whether the user has relevant permission to perform certain action.
    verify_token_proc = subprocess.run(['unmunge'], input=token, capture_output=True)
    for line in verify_token_proc.stdout.decode('utf-8').splitlines():
        if line.startswith('GID') and 'sudo' in line:
            return
    raise Exception('non-sudo user')
