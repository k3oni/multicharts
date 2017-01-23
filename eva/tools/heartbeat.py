#!/usr/bin/python
################################################################################

from logger import infor
import threading, time

class heartBeat:

    def __init__(self, name, period, msg):
        self.period = period
        self.msg = msg
        self.name = name
        self.hb = threading.Thread(group=None, target=self.echo, name=name)
        self.hb.daemon = False
        self.stop = False

    def echo(self):
        while True:
            infor(self.msg)
            time.sleep(self.period)
            if self.stop:
                return

    def start(self):
        self.hb.start()

    def stop(self):
        self.stop = True
        self.hb.join()
        infor('Heart beat stop.')


# Unit test
if __name__ == "__main__":
    hb = heartBeat("Test1", 1, "Heart Beat.")
    hb.start()
    infor('Sleeping ... ')
    time.sleep(8)
    infor('Wake up')
    hb.stop()
