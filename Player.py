#!/usr/bin/env python3
import socket
import sched, time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ('localhost', 10110)

log_file = "Vega-07.log"


##  17939076 <$GPRMC,135218.00,A,4703.84791,N,00654.17033,E,82.429,238.68,300706,,,A*50>
def toNMEA(line):
    parts = (" ".join(line.split()).split())
    ts = int(parts[0])
    nmea = parts[1][1:-1]
    return ts, nmea


def send(nmea):
    sock.sendto(f'{nmea}\n'.encode(), addr)

## stolen from: https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    print('\r[%s] %s%s ...%s' % (bar, percents, '%', suffix), end='', flush=True)


sched = sched.scheduler(time.time, time.sleep)
startTime = time.time()
baseTime = None
num_lines = sum(1 for line in open(log_file))

with open(log_file, "r") as logfile:
    for cnt, line in enumerate(logfile):
        progress(cnt, num_lines)
        ts, nmea, = toNMEA(line)
        if baseTime is None:
            baseTime = ts
        assert ts > 0, "Wrong time increment"
        sched.enterabs(startTime + (float(ts - baseTime)) / 1000.0, 1, lambda x: send(x), (nmea,))
        sched.run()
