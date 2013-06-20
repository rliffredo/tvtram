import bs4
import urllib.request
import codecs

def get_soup(url):
    request = urllib.request.urlopen('http://rozklady.mpk.krakow.pl/aktualne/' + url)
    return bs4.BeautifulSoup(request.readall())
    
class Stop:
    def __init__(self, name, link):
        self.name = name
        self.link = link

def scrap_stops():
    soup = get_soup('przystan.htm')
    stops = soup.select('table a')
    result = [ ]
    for stop in stops:
        if stop.get('href') is None:
            continue
        result.append(Stop(stop.text, stop.get('href')))
    return result

def parse_line_with_direction(text):
    # '123 - > asd'
    split = text.split(' ')
    return (split[0], split[3])

class StopLine:
    def __init__(self, stop, line, destination, link):
        self.stop = stop
        self.line = line
        self.destination = destination
        self.link = link

def scrap_stop_lines(stop):
    soup = get_soup(stop.link)
    directions = soup.select('table a')
    result = [ ]
    for dir in directions:
        if dir.get('href') == '../przystan.htm':
            continue
        details = parse_line_with_direction(dir.text)
        result.append(StopLine(stop, details[0], details[1], dir.get('href')[3:]))
    return result
    
class Schedule:
    def __init__(self, stop_line):
        self.stop_line = stop_line
        self.departures = [ ]

def scrap_schedule(stop_line):
    # build the link: r is the version with frames, t is without frames
    # there is only one r in the link
    link = stop_line.link.replace('r', 't')
    schedule = Schedule(stop_line)
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
            schedule.departures.append(hour + ':' + min)
    return schedule

def get_schedules_for_stop(stops, name):
    stop = next(stop for stop in stops if stop.name == name)
    stop_lines = scrap_stop_lines(stop)
    stop_schedules = [scrap_schedule(line) for line in stop_lines]
    return stop_schedules

def get_schedules():
    stops = scrap_stops()
    schedules = {}
    rondo_matecznego = 'Rondo Matecznego'
    lagiewniki = b"\xc5\x81agiewniki".decode('utf-8')
    rzemieslnicza = b'Rzemie\xc5\x9blnicza'.decode('utf-8')
    schedules[rondo_matecznego] = get_schedules_for_stop(stops, rondo_matecznego)
    schedules[lagiewniki] = get_schedules_for_stop(stops, lagiewniki)
    schedules[rzemieslnicza] = get_schedules_for_stop(stops, rzemieslnicza)
    return schedules


schedule = get_schedules()

print(schedule[0].stop_line.stop.name)
print(schedule[0].stop_line.line)
print(schedule[0].stop_line.destination)
print(schedule[0].departures)
