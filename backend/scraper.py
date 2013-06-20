import bs4
import urllib.request
import codecs
import json
import concurrent.futures

workers_get_schedules = 3
workers_scrap_stop_to = 10

def prints(text):
    #print(text.encode('ascii', 'ignore'))
    pass

def get_soup(url):
    request = urllib.request.urlopen('http://rozklady.mpk.krakow.pl/aktualne/' + url)
    return bs4.BeautifulSoup(request.readall())
    
class StopLine:
    def __init__(self, number, destination, link):
        self.number = number
        self.destination = destination
        self.link = link
        self.departures = [ ]
    
class Stop:
    def __init__(self, name, link):
        self.name = name
        self.link = link
        self.lines = [ ]

def scrap_stops():
    soup = get_soup('przystan.htm')
    stops = soup.select('table a')
    result = [ ]
    for stop in stops:
        if stop.get('href') is None:
            continue
        # prints('found stop: ' + stop.text)
        result.append(Stop(stop.text, stop.get('href')))
    return result

def parse_line(text):
    # '123 - > asd zxc'
    return tuple(text.split(' - > '))

def process_stop_line(line):
    if line.get('href') == '../przystan.htm':
        return
    number, direction = parse_line(line.text)
    link = line.get('href')[3:]
    stop_line = StopLine(number, direction, link)
    scrap_line_to(stop_line)
    return stop_line

def scrap_stop_to(stop):
    prints('scraping stop: ' + stop.name)
    soup = get_soup(stop.link)
    lines = soup.select('table a')
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers_scrap_stop_to) as executor:
        futures = [ executor.submit(process_stop_line, line) for line in lines ]
        results = [ future.result() for future in concurrent.futures.as_completed(futures) ]
        stop.lines = [ result for result in results if result is not None ]
    
def scrap_line_to(stop_line):
    prints('scraping line: ' + stop_line.number + ' ' + stop_line.destination)
    # build the link: r is the version with frames, t is without frames
    # there is only one r in the link
    link = stop_line.link.replace('r', 't')
    soup = get_soup(link)
    # skip the header and the footer
    rows = soup.select('td.celldepart tr')[1:-1]
    for row in rows:
        tds = row.select('td')
        hour = tds[0].text
        minutes = tds[1].text.split(' ')
        for min in minutes:
            if min == '-' or min == '':
                continue
            stop_line.departures.append(hour + ':' + min)
    prints(' '.join(stop_line.departures))

def stop_to_dictionary(stop):
    d = {}
    d['name'] = stop.name
    d['lines'] = [ ]
    for line in stop.lines:
        l = { }
        l['number'] = line.number
        l['destination'] = line.destination
        l['departures'] = line.departures[:]
        d['lines'].append(l)
    return d

def get_schedules_for_stop(stops, name):
    stop_data = next(stop for stop in stops if stop.name == name)
    scrap_stop_to(stop_data)
    return stop_to_dictionary(stop_data)

def get_schedules(stop_names):
    stops = scrap_stops()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers_get_schedules) as executor:
        futures = [ executor.submit(get_schedules_for_stop, stops, stop_name) for stop_name in stop_names ]
        results = [ future.result() for future in concurrent.futures.as_completed(futures) ]
        schedules = {
            'stops': results
        }
        return schedules

def get_specific_schedules():
    return get_schedules([ 'Rondo Matecznego', b'\xc5\x81agiewniki'.decode('utf-8'), b'Rzemie\xc5\x9blnicza'.decode('utf-8') ])

if __name__ == '__main__':
    schedule = get_specific_schedules()
    json_data = json.dumps(schedule)
    
    print(json_data)
    
    #import timeit
    #print(timeit.timeit("get_specific_schedules()", setup="from __main__ import get_specific_schedules", number=5))
