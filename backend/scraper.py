import bs4
import urllib.request
import codecs
import json

def prints(text):
    # print(text.encode('ascii', 'ignore'))
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
    # '123 - > asd'
    i = text.index(' - > ')
    return (text[0:i], text[i+5:])

def scrap_stop_to(stop):
    prints('scraping stop: ' + stop.name)
    soup = get_soup(stop.link)
    lines = soup.select('table a')
    for line in lines:
        if line.get('href') == '../przystan.htm':
            continue
        number, direction = parse_line(line.text)
        link = line.get('href')[3:]
        stop_line = StopLine(number, direction, link)
        scrap_line_to(stop_line)
        stop.lines.append(stop_line)
    
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

def get_schedules():
    stops = scrap_stops()
    rondo_matecznego = 'Rondo Matecznego'
    lagiewniki = b"\xc5\x81agiewniki".decode('utf-8')
    rzemieslnicza = b'Rzemie\xc5\x9blnicza'.decode('utf-8')
    schedules = {
        'stops': [
            get_schedules_for_stop(stops, rondo_matecznego),
            get_schedules_for_stop(stops, lagiewniki),
            get_schedules_for_stop(stops, rzemieslnicza)
        ]
    }
    return schedules


schedule = get_schedules()
json_data = json.dumps(schedule)

print(json_data)