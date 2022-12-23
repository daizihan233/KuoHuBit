import yaml


def get_config(name: str):
    try:
        y = yaml.load(open('config.yaml', 'r', encoding='UTF-8'), yaml.SafeLoader)
        return y[name]
    except KeyError:
        return None