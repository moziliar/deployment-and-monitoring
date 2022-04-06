import time
import textwrap
from collections import defaultdict


class Machine:
    def __init__(self, nodename):
        self.nodename = nodename
        self.num_cpu = 0

        # dynamic measures
        self.students = {}
        self.instructors = {}
        self.is_up = False
        self.system_load = [0, 0, 0]
        self.cpu_usage = None
        self.memory = None

    def get_num_users(self):
        return len(self.students) + len(self.instructors)

    def parse_top(self, top_output):
        self.is_up = True
        top_output = sanitize(top_output)
        [first, _, third, *_] = top_output.split('\\n')
        [_, system_load] = first.split('load average:')
        self.system_load = [raw.strip(',') for raw in system_load.split(' ')]
        third = third.split(':')[1].strip()
        [user, sys, nice, idle, io, irq, softirq, steal] = [w.strip().split(' ')[0] for w in third.split(',')]
        self.cpu_usage = CPU(user, sys, nice, idle, io, irq, softirq, steal)

    def get_cpu_usage(self):
        usage = self.cpu_usage
        if usage is None:
            return ''
        return f'overall: {usage.get_overall_usage():.1f}%, user: {usage.user:.1f}%, system: {usage.sys:.1f}%'

    def get_load_average(self):
        load = self.system_load
        return f'1min: {load[1]}, 5min: {load[2]}, 10min: {load[3]}'

    def parse_ps(self, ps_output):
        self.is_up = True
        self.students = defaultdict(User)
        ps_output = sanitize(ps_output)
        for line in str(ps_output).split('\\n')[1:]:
            if line == '':
                continue
            [pid, user, group, time, tty, cpu] = [s for s in line.split(' ') if s.strip()]
            self.students[user].add_proc(Process(pid, '', time, cpu))
        # TODO: implement instructor

    def parse_memory(self, free_output):
        self.is_up = True
        self.memory = Memory(*[s.strip("\\n'") for s in free_output.split(' ') if s.strip()][1:])

    def get_memory(self):
        mem = self.memory
        if mem is None:
            return ''
        return f'total: {mem.total}, used: {mem.used}, shared: {mem.shared}, cache: {mem.buff_cache}, \
avail: {mem.available}'

    def generate_report(self):
        status = '🟢' if self.is_up else '🔴'
        report = f'<b>{self.nodename}</b> {status}'
        if self.is_up:
            report += f""" (# of students : {len(self.students)})\n\
cpu usage: {self.get_cpu_usage()};\n\
memory: {self.get_memory()}\n\
"""
        else:
            report += '\n'
        return textwrap.dedent(report)


def sanitize(output: str):
    return output.lstrip("b'").rstrip("'")


class CPU:
    def __init__(self, user, sys, nice, idle, io, irq, softirq, steal):
        self.user = float(user)
        self.sys = float(sys)
        self.nice = float(nice)
        self.idle = float(idle)
        self.io = float(io)
        self.irq = float(irq)
        self.softirq = float(softirq)
        self.steal = float(steal)

    def get_overall_usage(self):
        return 100 - self.idle


class Memory:
    def __init__(self, total, used, free, shared, buff_cache, available):
        self.total = total
        self.used = used
        self.free = free
        self.shared = shared
        self.buff_cache = buff_cache
        self.available = available


class Process:
    def __init__(self, pid, cmd, _time, cpu):
        self.pid = pid
        self.cmd = cmd
        self.time = time.strptime(_time, '%H:%M:%S')
        self.cpu = float(cpu)


class User:
    def __init__(self):
        self.cpu_usage = 0
        self.ps = []

    def add_proc(self, proc: Process):
        self.ps.append(proc)
        self.cpu_usage += proc.cpu

