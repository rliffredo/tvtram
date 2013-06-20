import bottle
import scraper

@bottle.get('/hello')
def get_hello():
    return 'Hello world!'
    
@bottle.get('/stops')
def get_stops():
    return schedules

schedules = scraper.get_schedules([
    'Rondo Matecznego',
    b"\xc5\x81agiewniki".decode('utf-8'),
    b'Rzemie\xc5\x9blnicza'.decode('utf-8')
])

bottle.run(host='localhost', port=8080, reloader=True)