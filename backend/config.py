import sys
PY2 = sys.version_info[0] == 2

if PY2:
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser

from os import path
app_root = path.split(sys.path[0])[0]
backend_root = path.join(app_root, 'backend')

config_file = open('stops.ini', 'r', encoding='cp65001')

cp = ConfigParser()
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

