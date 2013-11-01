import sys
from os import path

PY2 = sys.version_info[0] == 2
if PY2:
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser

# Some patch for python 2 cp65001 bug
if PY2:
    import codecs
    def cp65001(name):
        if name.lower()=='cp65001':
            return codecs.lookup('utf-8')
    codecs.register(cp65001)

def get_defined_stops():
    app_root = path.split(sys.path[0])[0]
    backend_root = path.join(app_root, 'backend')

    cp = ConfigParser()
    with open('stops.ini', 'r', encoding='cp65001') as config_file: # windows utf-8
        cp.read_file(config_file)

    stops = []
    for section_name in cp.sections():
        config_data = cp[section_name]
        stop_data = {}
        for key in config_data:
            if key == 'name':
                stop_data[key] = config_data[key]
            elif key == 'pane':
                stop_data[key] = config_data[key]
            else:
                stop_data[key] = int(config_data[key])
        stops.append(stop_data)

    return stops

stops = get_defined_stops()
