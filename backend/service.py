import bottle
import scraper
import threading
import time

schedules = None

@bottle.get('/hello')
def get_hello():
    return 'Hello world!'

@bottle.route('<filepath:path>')
def get_static(filepath):
    if filepath=='/':
        return bottle.static_file('index.html', root=r'c:\users\roberto\repos\tvtram\html')
    return bottle.static_file(filepath, root=r'c:\users\roberto\repos\tvtram\html')

@bottle.get('/stops')
def get_stops():
    global schedules
    if schedules is None:
        bottle.abort(text='Initialization in progress')
    #print (schedules)
    return schedules

def get_new_schedules():
    try:
        new_schedules = scraper.get_schedules([
            'Rondo Matecznego',
            b"\xc5\x81agiewniki".decode('utf-8'),
            b'Rzemie\xc5\x9blnicza'.decode('utf-8')
        ])
        return new_schedules
    except Exception as e:
        print (e)
        pass # Ignore errors on this thread and go on...

def update_schedules():
    while (True):
        new_schedule = get_new_schedules()
        global schedules
        schedules = new_schedule
        time.sleep(60 * 60 * 12)

scraping_thread = threading.Thread(target=update_schedules)
scraping_thread.daemon = True
scraping_thread.start()

bottle.run(host='localhost', port=8080, reloader=True, debug=True)