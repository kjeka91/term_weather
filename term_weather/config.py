import configparser
import os

CONFIG_LOCATION = os.path.expanduser(os.path.join('~', '.config', 'term_weather'))
DEFAULTS = """[DEFAULT]
show_precipitation_now=True
show_forecast_row=True
bar_height=5
bar_width=5
language=en"""


def install_default_config(name, location, language):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string(DEFAULTS)
    config.add_section(name)
    config[name]["location"] = location
    config[name]["default"] = "True"
    config[name]["language"] = language
    if not os.path.exists(CONFIG_LOCATION):
        os.makedirs(CONFIG_LOCATION)

    with open(os.path.join(CONFIG_LOCATION, 'config'), 'w') as configfile:
        config.write(configfile)


def add_location(name, location, default):
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIG_LOCATION, 'config'))
    config.add_section(name)
    config[name]["location"] = location
    config[name]["default"] = default

    with open(os.path.join(CONFIG_LOCATION, 'config'), 'w') as configfile:
        config.write(configfile)


def list_places():
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIG_LOCATION, 'config'))
    for section in config.sections():
        try:
            if config[section]['default'] == 'True':
                default = '[DEFAULT]'
            else:
                default = ''
        except:
            default = ''

        print(section + ': ' + config[section]['location'] + ' ' + default)


def get_config(name):
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIG_LOCATION, 'config'))
    return config[name]


def get_default_config():
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIG_LOCATION, 'config'))
    for section in config.sections():
        try:
            if config[section]['default'] == 'True':
                return config[section]
        except KeyError:
            pass
    raise ValueError()


def set_default_location(location):
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIG_LOCATION, 'config'))
    for section in config.sections():
        if section == location:
            config[section]['default'] = 'True'
        else:
            config[section]['default'] = 'False'
    with open(os.path.join(CONFIG_LOCATION, 'config'), 'w') as configfile:
        config.write(configfile)