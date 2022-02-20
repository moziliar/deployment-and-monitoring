from copy import deepcopy
from string import Template

_sync_user_play = {
    'name': 'Update lab machines',
    'hosts': 'TODO',
    'remote_user': 'TODO',
    'tasks': []
}

# User info section
_user_info = {
    'name': 'TODO',
    'group': 'TODO',

    'umask': '077',
    'shell': '/bin/bash',
}

_remove_password = {
    'name': Template('remove user $username password'),
    'command': Template('passwd -d $username')
}

_expire_password = {
    'name': Template('expire user $username password to update upon first login'),
    'command': Template('chage -d 0 $username')
}

# Remove user task ensures the user and the home dir no longer exist
_remove_user_suffix = {
    'state': 'absent', # require user to be absent
    'remove': True, # remove homedir
}

def get_sync_user_play(hosts, remote_user, users_to_add, users_to_remove):
    if not users_to_add and not users_to_remove:
        return None
    new_play = deepcopy(_sync_user_play)
    new_play['hosts'] = hosts
    new_play['remote_user'] = remote_user

    new_play['tasks'] += map(lambda u: get_add_user_task(u.name, u.group), users_to_add)
    new_play['tasks'] += map(lambda u: get_remove_user_task(u.name, u.group), users_to_remove)
    
    # For new users, remove password and prompt for password change upon first login
    new_play['tasks'] += map(lambda u: get_remove_user_password(u.name), users_to_add)
    new_play['tasks'] += map(lambda u: get_expire_user_password(u.name), users_to_add)
    return new_play

def get_user_info(name, group):
    new_user = deepcopy(_user_info)
    new_user['name'] = name
    new_user['group'] = group
    return new_user

def get_add_user_task(name, group):
    return {
        'name': f'add user {name}',
        'ansible.builtin.user': get_user_info(name, group)
    }

def get_remove_user_task(name, group):
    return {
        'name': f'remove user {name}',
        'ansible.builtin.user': get_user_info(name, group) | _remove_user_suffix
    }
def get_remove_user_password(name):
    remove_password = deepcopy(_remove_password)
    remove_password['name'] = remove_password['name'].substitute(username=name)
    remove_password['command'] = remove_password['command'].substitute(username=name)
    return remove_password

def get_expire_user_password(name):
    expire_password = deepcopy(_expire_password)
    expire_password['name'] = expire_password['name'].substitute(username=name)
    expire_password['command'] = expire_password['command'].substitute(username=name)
    return expire_password


_sync_software_play = {
    'name': 'Update lab machines',
    'hosts': 'TODO',
    'remote_user': 'TODO',
    'tasks': []
}

def get_install_software(software, version='latest'):
    return {
        'name': f'Ensure {software} is installed and at version specified',
        'ansible.builtin.apt': {
            'name': software,
            'version': version
        }
    }

def get_sync_software_play(hosts, remote_user, softwares_to_install):
    new_play = deepcopy(_sync_software_play)
    new_play['hosts'] = hosts
    new_play['remote_user'] = remote_user

    new_play['tasks'] += map(lambda s: get_install_software(s.name, s.version), softwares_to_install)
    return new_play
