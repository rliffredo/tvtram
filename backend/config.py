import sys
from os import path

PY2 = sys.version_info[0] == 2
if PY2:
    from io import open
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
    with open(path.join(backend_root, 'stops.ini'), 'r', encoding='cp65001') as config_file: # windows utf-8
        if PY2:
            cp.readfp(config_file)
        else:
            cp.read_file(config_file)

    stops = []
    for section_name in cp.sections():
        stop_configuration = cp.items(section_name)
        stop_data = {}
        for key, value in stop_configuration:
            if key in ('name', 'pane'):
                stop_data[key] = value
            else:
                stop_data[key] = int(value)
        stops.append(stop_data)

    return stops

stops = get_defined_stops()
