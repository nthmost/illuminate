import time, os

def select_file_from_aliases(codename, filemap, basepath):
    "acquires first physical file available in dataset matching codename."
    #assume that list in filemap has first item as most likely file.
    for item in filemap[codename]:
        filepath = os.path.join(basepath, item)
        if os.path.exists(filepath):
            return filepath
    # none of the possible files extant
    return None

def dmesg(msg, lvl=1):
    VERBOSITY = 1
    DEBUG = True
    "Simple logger - transitional code."
    msg = "[%s] " % str(time.time()) + str(msg)
    if DEBUG: msg = "[DEBUG] " + msg
    if VERBOSITY >= lvl:
        print msg
    
