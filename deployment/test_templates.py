import unittest
import yaml

import templates
from usergroup import User

class AnsibleUserTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_get_add_user_task(self):
        self.assertEqual(
            to_yaml_str(templates.get_add_user_task('test1', 'tg')), 
"""ansible.builtin.user:
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
"""ansible.builtin.user:
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
            to_yaml_str(templates.get_sync_user_play(users_to_add, users_to_remove)), 
"""hosts: TODO
name: Update lab machines
remote_user: TODO
tasks:
- ansible.builtin.user:
    group: tg1
    name: test1
    shell: /bin/bash
    umask: '077'
  name: add user test1
- ansible.builtin.user:
    group: tg1
    name: test2
    shell: /bin/bash
    umask: '077'
  name: add user test2
- ansible.builtin.user:
    group: tg2
    name: test3
    shell: /bin/bash
    umask: '077'
  name: add user test3
- ansible.builtin.user:
    group: tg3
    name: test4
    remove: true
    shell: /bin/bash
    state: absent
    umask: '077'
  name: remove user test4
- ansible.builtin.user:
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


def to_yaml_str(json_str):
    return yaml.dump(json_str)
