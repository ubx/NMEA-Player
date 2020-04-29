#!/usr/bin/env python3
import argparse
import socket
import sched, time

parser = argparse.ArgumentParser(
    'python NMAE Player',
    description='Replay a nmea logfile with timestamp to udp (default: localhost, 10110).')
parser.add_argument('logfile', metavar='logfile', type=str)
parser.add_argument('-address', metavar='address', type=str, default='localhost',
                    help='UDP address (default localhost)')
parser.add_argument('-port', metavar='port', type=int, default=1011, help='UDP port (default 1011)')
results = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = (results.address, results.port)


##  17939076 <$GPRMC,135218.00,A,4703.84791,N,00654.17033,E,82.429,238.68,300706,,,A*50>
def toNMEA(line):
    parts = (' '.join(line.split()).split())
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
log_file = results.logfile
num_lines = sum(1 for line in open(log_file))

with open(log_file, "r") as logfile:
    for cnt, line in enumerate(logfile):
        ts, nmea, = toNMEA(line)
        assert ts > 0, 'Wrong time increment'
        progress(cnt, num_lines, ts)
        if baseTime is None:
            baseTime = ts
        sched.enterabs(startTime + (float(ts - baseTime)) / 1000.0, 1, lambda x: send(x), (nmea,))
        sched.run()
