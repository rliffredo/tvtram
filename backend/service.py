import bottle
import scraper_mpk as scraper
import threading
import time

import config

schedules = None

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
    if schedules is None:
        bottle.abort(text='Initialization in progress')
    return {'data': schedules, 'specs': config.stops}

def get_new_schedules():
    try:
        return scraper.get_schedules([stop['name'] for stop in config.stops])
    except Exception as e:
        print("Exception encountered while getting new schedules", file=sys.stderr)
        print(e, file=sys.stderr)
        return None # Ignore errors on this thread and go on...

def update_schedules():
    while (True):
        global schedules
        schedules = get_new_schedules()
        if schedules is not None:
            time.sleep(60 * 60 * 12)
        else:
            print ("Reloading time table...")
            time.sleep(1)

scraping_thread = threading.Thread(target=update_schedules)
scraping_thread.daemon = True
scraping_thread.start()

bottle.run(host='localhost', port=8080, reloader=False, debug=True)