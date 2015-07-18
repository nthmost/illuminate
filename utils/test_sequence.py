from illuminate import InteropDataset, InteropFileNotFoundError
import os
import sys


try:
    rootdir = sys.argv[1]
except:
    print "Supply path as argument to this script."
    sys.exit()

sequence = os.listdir(rootdir)

for item in sequence:
    id = InteropDataset(os.path.join(rootdir, item))
    print "DATASET: %r\n" % item
    try:
        print "-> TILE"
        print id.TileMetrics()
    except InteropFileNotFoundError:
        print "not found"

    print "-> QUALITY"
    try:
        qm = id.QualityMetrics()
        print qm
    except InteropFileNotFoundError:
        print "not found"

    print "-> EXTRACTION"
    try:
        em = id.ExtractionMetrics()
        print em
    except InteropFileNotFoundError:
        print "not found"

    print ""
    print "=============="
    print ""

