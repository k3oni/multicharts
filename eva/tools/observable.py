#/usr/bin/python
################################################################################

class observable:

    def __init__(self):
        self.eventObvList = dict()

    def register(self, msg, observer):
        obs = []
        if msg not in self.eventObvList.keys():
            obs = obs.append(observer)
            self.eventObvList[msg] = obs
        else:
            self.eventObvList[msg].append(observer)

    def notify(self, msg):
        obs = self.eventObvList.get(msg)
        for o in obs:
            obs.onEvent(msg)
        
class observer:

    def __init__(self):
        pass

    def onEvent(self, msg):
        pass

