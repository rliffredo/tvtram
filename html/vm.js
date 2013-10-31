if (Array.prototype.filter === undefined) {
    Array.prototype.filter = function (callback) {
        var result = [];
        var i = 0;
        for (i = 0; i < this.length; i++) {
            if (callback(this[i], i, this)) {
                result.push(this[i]);
            }
        }
        return result;
    }
}
var getCurrentTime = function () {
    var d = new Date();
    return d;
};

var getDepartureTime = function (now, dep) {
    var parts = dep.time.split(':');
    var hours = parseInt(parts[0], 10);
    var minutes = parseInt(parts[1], 10);
    var departureTime = new Date(now.getTime());
    departureTime.setHours(hours);
    departureTime.setMinutes(minutes);
    // roll over day
    if (departureTime < now) {
        departureTime.setDate(departureTime.getDate() + 1);
    }
    return departureTime;
};

var minutesTillDeparture = function (now, dep) {
    var departureTime = getDepartureTime(now, dep);
    var diffMs = departureTime.getTime() - now.getTime();
    var diffMin = Math.floor(diffMs / 1000 / 60);
    return diffMin;
};

var stringCompare = function (left, right) {
    return left === right
        ? 0
        : (left < right ? -1 : 1);
};

var updateTime = function (stop, now) {
    var entries = 0, i = 0;
    stop.allDepartures.forEach(function (dep) {
        dep.minutesLeft(minutesTillDeparture(now, dep));
    });
    stop.allDepartures.sort(function (left, right) {
        var res = left.minutesLeft() - right.minutesLeft();
        if (res != 0) {
            return res;
        }
        var res = stringCompare(left.number, right.number);
        if (res != 0) {
            return res;
        }
        return stringCompare(left.destination, right.destination);
    });

    stop.departures.removeAll();
    while (entries < stop.max_entries) {
        var dep = stop.allDepartures[i++];
        if (dep.minutesLeft() < stop.min_time) {
            continue;
        }
        stop.departures.push(dep);
        ++entries;
    }
};

var createStopVm = function (allData, spec) {
    var stop = allData.stops.filter(function (stop) {
        return stop.name === spec.name;
    })[0];
    stop.pane = spec.pane;
    stop.max_entries = spec.max_entries;
    stop.min_time = spec.min_time;
    stop.hurry_time = spec.hurry_time;
    stop.medium_time = spec.medium_time;
    stop.departures.forEach(function (dep) {
        dep.type = dep.number.length > 2 ? 'bus' : 'tram';
        // minutes till departure
        dep.minutesLeft = ko.observable(0);
        dep.timeLeft = ko.computed(function () {
            return this.minutesLeft() + ' min';
        }, dep);
        dep.warning = ko.computed(function () {
            var minLeft = this.minutesLeft();
            if (minLeft <= stop.hurry_time) {
                return 'hurry';
            } else if (minLeft <= stop.medium_time) {
                return 'medium';
            } else {
                return 'easy';
            }
        }, dep);
    });
    stop.allDepartures = stop.departures;
    stop.departures = ko.observableArray([]);
    return stop;
};

var createVm = function (data, specs) {
    var vm = {
        stopVms: specs.map(function (spec) { return createStopVm(data, spec); }),
        currentTime: ko.observable('00:00')
    };

    var formatHHMM = function (time) {
        var hours = '00' + time.getHours().toString();
        var minutes = '00' + time.getMinutes().toString();
        return hours.slice(-2) + ':' + minutes.slice(-2);
    };

    vm.updateStops = function (now) {
        this.stopVms.forEach(function (vm) { updateTime(vm, now) });
    };

    vm.updateClock = function (now) {
        this.currentTime(formatHHMM(now));
    };

    return vm;
};

var calculateNextRefresh = function () {
    var now = getCurrentTime();
    return 60 - now.getSeconds();
};

var updateView = function () {
    var now = getCurrentTime();
    updateStops(now);
    updateClock(now);
    setTimeout(function () { updateView(); }, calculateNextRefresh() * 1000);
}

var initialize = function () {
    $.get('http://localhost:8080/stops')
        .done(function (res) {
            specs = res.specs;
            data = res.data;
            var vm = createVm(data, specs);
            updateStops = vm.updateStops.bind(vm);
            updateClock = vm.updateClock.bind(vm);
            updateView();
            ko.applyBindings(vm);
        })
        .fail(function () {
            setTimeout(initialize, 250)
        });
};
