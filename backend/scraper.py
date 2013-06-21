import sys
PY2 = sys.version_info[0] == 2

if PY2:
    from urllib2 import urlopen
else:
    from urllib.request import urlopen


import bs4
import codecs
import json
import concurrent.futures

workers_get_schedules = 3
workers_scrap_stop = 10

class Departure:
    def __init__(self, number, destination, time, alt_route):
        self.number = number
        self.destination = destination
        self.time = time
        self.alt_route = alt_route
    
    def __str__(self):
        return str.format('{0} {1} {2}{3}', self.number, self.destination, self.time, '*' if self.alt_route else '')
    
class Stop:
    def __init__(self, name):
        self.name = name
        self.departures = [ ]

def get_soup(url):
    request = urlopen('http://rozklady.mpk.krakow.pl/aktualne/' + url)
    return bs4.BeautifulSoup(request.read())

def scrap_stops():
    soup = get_soup('przystan.htm')
    stops = soup.select('table a')
    result = [ ]
    for stop in stops:
        if stop.get('href') is None:
            continue
        result.append((stop.text, stop.get('href')))
    return result

def parse_line(text):
    # '123 - > asd zxc'
    return tuple(text.split(' - > '))
    
def scrap_line(number, destination, link):
    # build the link: r is the version with frames, t is without frames
    # there is only one r in the link
    link = link.replace('r', 't')
    soup = get_soup(link)
    # skip the header and the footer
    rows = soup.select('td.celldepart tr')[1:-1]
    departures = [ ]
    for row in rows:
        tds = row.select('td')
        hour = tds[0].text.zfill(2)
        minutes = tds[1].text.split(' ')
        for min_part in minutes:
            if min_part == '-' or min_part == '':
                continue
            min = min_part[0:2].zfill(2)
            suffix = min_part[2:]
            time = hour + ':' + min
            departures.append(Departure(number, destination, time, len(suffix) > 0))
    return departures    

def process_stop_line(line):
    if line.get('href') == '../przystan.htm':
        return None
    number, destination = parse_line(line.text)
    link = line.get('href')[3:]
    return scrap_line(number, destination, link)

def scrap_stop(name, link):
    soup = get_soup(link)
    stop = Stop(name)
    lines = soup.select('table a')
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers_scrap_stop) as executor:
        futures = [ executor.submit(process_stop_line, line) for line in lines ]
        results = [ future.result() for future in concurrent.futures.as_completed(futures) if future.result() is not None ]
        for res in results:
            stop.departures.extend(res)
        stop.departures.sort(key=lambda d: d.time)
        return stop

def stop_to_dictionary(stop):
    s = { }
    s['name'] = stop.name
    s['departures'] = [ ]
    for dep in stop.departures:
        d = { }
        d['number'] = dep.number
        d['destination'] = dep.destination
        d['time'] = dep.time
        d['altRoute'] = dep.alt_route
        s['departures'].append(d)
    return s

def get_schedules_for_stop(stops_data, stop_name):
    stop_data = next(sd for sd in stops_data if sd[0] == stop_name)
    stop = scrap_stop(stop_data[0], stop_data[1])
    return stop_to_dictionary(stop)

def get_schedules(stop_names):
    stops_data = scrap_stops()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers_get_schedules) as executor:
        futures = [ executor.submit(get_schedules_for_stop, stops_data, stop_name) for stop_name in stop_names ]
        results = [ future.result() for future in concurrent.futures.as_completed(futures) ]
        schedules = {
            'stops': results
        }
        return schedules

if __name__ == '__main__':

    def get_specific_schedules():
        return get_schedules([
            'Rondo Matecznego',
            b'\xc5\x81agiewniki'.decode('utf-8'),
            b'Rzemie\xc5\x9blnicza'.decode('utf-8')
        ])

    schedule = get_specific_schedules()
    json_data = json.dumps(schedule)
    
    print(json_data)
    
    #import timeit
    #print(timeit.timeit("get_specific_schedules()", setup="from __main__ import get_specific_schedules", number=5))
