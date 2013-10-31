import bottle
import scraper
import threading
import time

import config

schedules = None
valid_stops = None

import sys
from os import path
app_root = path.split(sys.path[0])[0]
html_root = path.join(app_root, 'html')

@bottle.get('/ping')
def get_ping():
    return 'pong!'

@bottle.route('<filepath:path>')
def get_static(filepath):
    if filepath=='/':
        return bottle.static_file('index.html', root=html_root)
    return bottle.static_file(filepath, root=html_root)

@bottle.get('/stops')
def get_stops():
    global schedules
    global valid_stops
    if schedules is None:
        bottle.abort(text='Initialization in progress')
    return {'specs': valid_stops, 'data': schedules}

def get_new_schedules():
    try:
        return scraper.get_schedules([stop['name'] for stop in config.stops])
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)
        pass # Ignore errors on this thread and go on...

def update_schedules():
    while (True):
        global schedules
        global valid_stops
        schedules, valid_stop_names = get_new_schedules()
        valid_stops = [stop_spec for stop_spec in config.stops if stop_spec['name'] in valid_stop_names]
        if schedules is not None:
            time.sleep(60 * 60 * 12)
        else:
            print ("Reloading time table...")
            time.sleep(1)

scraping_thread = threading.Thread(target=update_schedules)
scraping_thread.daemon = True
scraping_thread.start()

bottle.run(host='localhost', port=8080, reloader=True, debug=True)