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

stops = scrap_stops()

def get_schedule(stops, name, line, destination):
    stop = next(stop for stop in stops if stop.name == name)
    stop_lines = scrap_stop_lines(stop)
    stop_line = next(sl for sl in stop_lines if sl.line == line and sl.destination == destination)
    return scrap_schedule(stop_line)

def get_


schedule = get_schedule(stops, 'Rondo Matecznego', '23', 'Czerwone Maki')

print(schedule.stop_line.stop.name)
print(schedule.stop_line.line)
print(schedule.stop_line.destination)
print(schedule.departures)
