import logging
import threading
import time
from datetime import datetime

from monitor.ssh import SSH
from monitor import (
    machine_command,
    machine
)

report = "-"
report_lock = threading.Lock()


class MonitorDaemon(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global report

        nodes_to_read = []
        with open('nodes.txt', 'r') as node_f:
            for line in node_f.readlines():
                nodes_to_read.append(line.strip('\n'))

        ssh = SSH()
        ssh.setup_connections_to_hosts(nodes_to_read)
        nodes = {node: machine.Machine(node) for node in nodes_to_read}
        while True:
            def exec_cmd(command, stdout_callback):
                for hostname, (output, success) in ssh.exec_on_all_machines(nodes_to_read, command).items():
                    if not success:
                        nodes[hostname].is_up = False
                        continue
                    err = output.stderr.read()
                    if len(err) > 0:
                        logging.error(err)
                        nodes[hostname].is_up = False
                        continue
                    out = output.stdout.read()
                    method = getattr(machine.Machine, stdout_callback)
                    try:
                        method(nodes[hostname], str(out))
                    except Exception as e:
                        logging.error(e)

            logging.info("exec_monitor_command")
            for cmd, callback in {
                machine_command.read_cpu: "parse_top",
                machine_command.read_ps: "parse_ps",
                machine_command.read_memory: "parse_memory"
            }.items():
                exec_cmd(cmd, callback)

            logging.info('generating_reports')
            _report = []
            for node in nodes.values():
                _report.append(node.generate_report())

            _report.append(f'Last updated at {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')

            report_lock.acquire()
            report = '\n'.join(_report)
            report_lock.release()

            logging.info(f'generated_{len(_report)}_reports')

            time.sleep(10)
