import unittest
import yaml
import templates

from usergroup import User
from software import Software


class AnsibleUserTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_get_add_user_task(self):
        self.assertEqual(
            to_yaml_str(templates.get_add_user_task('test1', 'tg')),
            """user:
  group: tg
  name: test1
  shell: /bin/bash
  umask: '077'
name: add user test1
""",
            'wrong task for add user')

    def test_get_remove_user_task(self):
        self.assertEqual(
            to_yaml_str(templates.get_remove_user_task('test1', 'tg')),
            """user:
  group: tg
  name: test1
  remove: true
  shell: /bin/bash
  state: absent
  umask: '077'
name: remove user test1
""",
            'wrong task for remove user')

    def test_get_sync_user_play(self):
        hosts = 'test-cluster'
        remote_user = 'admin'
        users_to_add = [
            User(name='test1', group='tg1'),
            User(name='test2', group='tg1'),
            User(name='test3', group='tg2')
        ]
        users_to_remove = [
            User(name='test4', group='tg3'),
            User(name='test5', group='tg3')
        ]

        self.assertEqual(
            to_yaml_str(templates.get_sync_user_play(hosts, remote_user, users_to_add, users_to_remove)),
            """hosts: test-cluster
name: Update lab machines
remote_user: admin
tasks:
- user:
    group: tg1
    name: test1
    shell: /bin/bash
    umask: '077'
  name: add user test1
- user:
    group: tg1
    name: test2
    shell: /bin/bash
    umask: '077'
  name: add user test2
- user:
    group: tg2
    name: test3
    shell: /bin/bash
    umask: '077'
  name: add user test3
- user:
    group: tg3
    name: test4
    remove: true
    shell: /bin/bash
    state: absent
    umask: '077'
  name: remove user test4
- user:
    group: tg3
    name: test5
    remove: true
    shell: /bin/bash
    state: absent
    umask: '077'
  name: remove user test5
- command: passwd -d test1
  name: remove user test1 password
- command: passwd -d test2
  name: remove user test2 password
- command: passwd -d test3
  name: remove user test3 password
- command: chage -d 0 test1
  name: expire user test1 password to update upon first login
- command: chage -d 0 test2
  name: expire user test2 password to update upon first login
- command: chage -d 0 test3
  name: expire user test3 password to update upon first login
""",
            'wrong play for user sync')

    def test_get_install_software_task(self):
        self.assertEqual(
            to_yaml_str(templates.get_install_software('gcc')),
            """apt:
  name: gcc
  state: latest
name: Ensure gcc is installed and at the latest version
""",
            'wrong task for software install')

    def test_get_sync_user_play(self):
        hosts = 'test-cluster'
        remote_user = 'admin'
        softwares_to_install = [
            Software(name='gcc'),
            Software(name='test-software'),
        ]

        self.assertEqual(
            to_yaml_str(templates.get_sync_software_play(hosts, remote_user, softwares_to_install)),
            """hosts: test-cluster
name: Update lab machines
remote_user: admin
tasks:
- apt:
    name: gcc
    state: latest
  name: Ensure gcc is installed and at the latest version
- apt:
    name: test-software
    state: latest
  name: Ensure test-software is installed and at the latest version
""")


def to_yaml_str(json_str):
    return yaml.dump(json_str)
