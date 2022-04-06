import logging
import os

import paramiko
from configs import config

port = 22
paramiko.util.log_to_file(config.sshLogPath)


class SSH:
    def __init__(self):
        self.ssh_conns = {}
        self.command = ''

    def register_command(self, command):
        self.command = command

    def setup_connection_to_host(self, hostname):
        if hostname in self.ssh_conns:
            return None

        logger = paramiko.util.logging.getLogger()
        logging.getLogger("paramiko").setLevel(logging.WARNING)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())

        # ssh_config = paramiko.SSHConfig()
        # user_config_file = os.path.expanduser("~/.ssh/config")
        # with io.open(user_config_file, 'rt', encoding='utf-8') as f:
        #     ssh_config.parse(f)
        # host_conf = ssh_config.lookup(hostname)
        # if host_conf:
        #     if 'proxycommand' in host_conf:
        #         cfg['sock'] = paramiko.ProxyCommand(host_conf['proxycommand'])

        key = paramiko.RSAKey.from_private_key_file(config.sshKeyPath, password=os.getenv("SSH_PASSWORD"))
        logging.info(f'connecting to {hostname}')
        client.connect(hostname=hostname, username=os.getenv("SSH_USER"), pkey=key, password=os.getenv("SSH_PASSWORD"))
        logging.info(f'connected to {hostname}')

        self.ssh_conns[hostname] = client

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


class SSHOutput:
    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr
