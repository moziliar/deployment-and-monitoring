import yaml
import rpyc


def save_yaml_data_to_path(data, filepath):
    with open(filepath, 'w') as f:
        data_dict = {}
        for data_entry in data.values():
            data_dict[data_entry.name] = rpyc.classic.obtain(data_entry).to_dict()
        yaml.safe_dump(data_dict, f, default_flow_style=False)
