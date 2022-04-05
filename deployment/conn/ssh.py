import logging
import os

import fabric.config
import paramiko
from paramiko import util
from configs import config

port = 22
if not os.path.exists(config.logDir):
    os.makedirs(config.logDir)
util.log_to_file(config.sshLogPath, level=logging.DEBUG)


class SSH(object):
    def __init__(self):
        self.ssh_conns = {}
        self.command = ''

    def register_command(self, command):
        self.command = command

    def setup_connection_to_host(self, hostname):
        if hostname in self.ssh_conns:
            return None

        real_hostname = hostname

        username = os.getenv('SSH_USER')
        password = os.getenv('SSH_PASSWORD')
        port = 22
        key_filename = None

        # config override
        custom_config_path = os.getenv('SSH_CONFIG_PATH')
        if custom_config_path:
            conf = paramiko.SSHConfig.from_path(custom_config_path)
            host = conf.lookup(hostname)

            # override values
            real_hostname = str(host['hostname'])
            username = host['user']
            password = None
            port = str(host['port'])
            key_filename = host['identityfile']

        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_client.connect(
            hostname=real_hostname,
            username=username,
            password=os.getenv('SSH_PASSWORD'),
            port=port,
            key_filename=key_filename,
            # pkey=key,
            # sock=paramiko.ProxyCommand(host.get('proxycommand')),
            timeout=5,
        )

        self.ssh_conns[hostname] = ssh_client

    def setup_connections_to_hosts(self, hostnames):
        for hostname in hostnames:
            try:
                self.setup_connection_to_host(hostname)
            except paramiko.AuthenticationException as err:
                logging.warning(f'{hostname} ssh authentication failed with err {err}')
            except paramiko.SSHException as err:
                logging.warning(f'{hostname} ssh setup failed with err {err}')
            except Exception as err:
                logging.error(f'{hostname} exec failed with err {err}')

    def exec_on_all_machines(self, hostnames, command):
        res = {}
        for hostname in hostnames:
            res[hostname] = self.exec_on_machine(hostname, command)
        return res

    def exec_on_machine(self, hostname, command):
        if hostname not in self.ssh_conns:
            try:
                self.setup_connection_to_host(hostname)
            except paramiko.AuthenticationException as err:
                logging.warning(f'{hostname} ssh authentication failed with err {err}')
                return None, False
            except paramiko.SSHException as err:
                logging.warning(f'{hostname} ssh setup failed with err {err}')
                return None, False
            except Exception as err:
                logging.error(f'{hostname} exec failed with err {err}')
                return None, False

        client = self.ssh_conns[hostname]
        _, stdout, stderr = client.exec_command(command)
        return SSHOutput(stdout, stderr), True


class SSHOutput(object):
    def __init__(self, stdout, stderr):
        self.stdout = stdout.read().decode('utf-8')
        self.stderr = stderr.read().decode('utf-8')


client = SSH()
