

def dmesg(self, msg, lvl=1):
    "Simple logger - transitional code."
    msg = "[%f] " % time.time() + msg
    if DEBUG: msg = "[DEBUG] " + msg
    if VERBOSITY >= lvl:
        print msg
    