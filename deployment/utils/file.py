import yaml
import rpyc


def save_yaml_data_to_path(data, filepath):
    with open(filepath, 'w+') as f:
        data_dict = {}
        for data_entry in data.values():
            data_dict[data_entry.name] = rpyc.classic.obtain(data_entry).to_dict()
        yaml.safe_dump(data_dict, f, default_flow_style=False)


def dump_to_playbook_at(path, data):
    with open(path, 'w+') as f:
        yaml.dump([data], f)


def generate_ini_file(host_map):
    from configparser import ConfigParser
    config = ConfigParser(allow_no_value=True)

    for group, hosts in host_map.items():
        config.add_section(group)
        for host in hosts:
            config.set(group, host)

    with open('resources/monitoring/hosts', 'w+') as f:
        config.write(f)
