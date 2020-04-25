#!/usr/bin/env python3
import socket
import sched, time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ('localhost', 10110)


##  17939076 <$GPRMC,135218.00,A,4703.84791,N,00654.17033,E,82.429,238.68,300706,,,A*50>
def toNMEA(line):
    parts = (" ".join(line.split()).split())
    ts = int(parts[0])
    nmea = parts[1][1:-1]
    return ts, nmea


def send(nmea):
    sock.sendto(f'{nmea}\n'.encode(), addr)


sched = sched.scheduler(time.time, time.sleep)
startTime = time.time()
baseTime = None
with open("Vega-07.log", "r") as logfile:
    for cnt, line in enumerate(logfile):
        ts, nmea, = toNMEA(line)
        if baseTime is None:
            baseTime = ts
        assert ts > 0, "Wrong time increment"
        sched.enterabs(startTime + (float(ts - baseTime)) / 1000.0, 1, lambda x: send(x), (nmea,))
        sched.run()
