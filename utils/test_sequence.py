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
   print id.TileMetrics()
   try:
       qm = id.QualityMetrics()
       print qm
   except InteropFileNotFoundError:
       print "not found"

