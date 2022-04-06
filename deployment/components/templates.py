from collections import defaultdict
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
    'state': 'absent',  # require user to be absent
    'remove': True,  # remove homedir
}


def get_sync_user_play(all_hosts, remote_user, users_to_add, users_to_remove):
    # Generate host group in host file
    host_map = {
        'all': [all_hosts]
    }
    if not users_to_add and not users_to_remove:
        return None, host_map

    # Find common hosts
    host_group_user_map = defaultdict(lambda: [[], []])
    for user_to_add, target_machines in users_to_add.items():
        host_group_user_map[tuple(target_machines)][0].append(user_to_add)

    for user_to_remove, target_machines in users_to_add.items():
        host_group_user_map[tuple(target_machines)][1].append(user_to_remove)

    machine_group_idx = 0

    new_book = []

    for host_group, [users_to_add, users_to_remove] in host_group_user_map.items():
        host_group_name = f'machine_group_{machine_group_idx}'
        host_map[host_group_name] = list(host_group)

        machine_group_idx += 1
        new_play = deepcopy(_sync_user_play)
        new_play['hosts'] = host_group_name
        new_play['remote_user'] = remote_user

        new_play['tasks'] += map(lambda u: get_add_user_task(u.name, u.group), users_to_add)
        new_play['tasks'] += map(lambda u: get_remove_user_task(u.name, u.group), users_to_remove)

        # For new users, remove password and prompt for password change upon first login
        new_play['tasks'] += map(lambda u: get_remove_user_password(u.name), users_to_add)
        new_play['tasks'] += map(lambda u: get_expire_user_password(u.name), users_to_add)

        print(new_play)
        new_book.append(new_play)

    print(new_book)
    return new_book, host_map


def get_user_info(name, group):
    new_user = deepcopy(_user_info)
    new_user['name'] = name
    new_user['group'] = group
    return new_user


def get_add_user_task(name, group):
    return {
        'name': f'add user {name}',
        'user': get_user_info(name, group)
    }


def get_remove_user_task(name, group):
    return {
        'name': f'remove user {name}',
        'user': {**get_user_info(name, group), **_remove_user_suffix}
    }


def get_remove_user_password(name):
    return {
        'name': _remove_password['name'].substitute(username=name),
        'command': _remove_password['command'].substitute(username=name)
    }


def get_expire_user_password(name):
    return {
        'name': _expire_password['name'].substitute(username=name),
        'command': _expire_password['command'].substitute(username=name)
    }


_sync_software_play = {
    'name': 'Update lab machines',
    'hosts': 'TODO',
    'remote_user': 'TODO',
    'tasks': []
}


def get_install_software(software):
    return {
        'name': f'Ensure {software} is installed and at the latest version',
        'apt': {
            'name': software,
            'state': 'latest',
            'update_cache': 'yes',
        }
    }


def get_sync_software_play(hosts, remote_user, softwares_to_install):
    if not softwares_to_install:
        return None
    print(softwares_to_install)
    new_play = deepcopy(_sync_software_play)
    new_play['hosts'] = 'all' # sync software to all machines
    new_play['remote_user'] = remote_user

    new_play['tasks'] += map(lambda s: get_install_software(s.name), softwares_to_install)
    print(new_play)
    return new_play
