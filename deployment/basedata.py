import yaml

yaml.SafeDumper.add_representer(
    type(None),
    lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
)


class Data(object):
    def __init__(self):
        self.filepath = ''

    @classmethod
    def open_yaml(cls, filepath):
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)

    def load_yaml(self, data):
        if not data:
            return
        for name, attr in data.items():
            self.load_object(name, attr)

    def load_object(self, name, attr):
        pass

    def get_data(self):
        pass

    def write_back(self):
        with open(self.filepath, 'w') as f:
            data_dict = {}
            for data_entry in self.get_data().values():
                data_dict[data_entry.name] = data_entry.to_dict()
            yaml.safe_dump(data_dict, f, default_flow_style=False)


class DataEntity(object):
    def __init__(self, name):
        self.name = name

    @classmethod
    def from_yaml(cls, key, val):
        u = cls(key)
        if type(val) != dict:
            return u
        for k, v in val.items():
            u.__setattr__(k, v)
        return u

    def to_dict(self):
        pass
