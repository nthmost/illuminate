import os

from illuminate.__main__ import main

ARGS = {
  "--all": True, 
  "--control": False, 
  "--corint": False, 
  "--csv": False, 
  "--debug": True, 
  "--error": False, 
  "--extraction": False, 
  "--help": False, 
  "--index": False, 
  "--interactive": False, 
  "--json": False, 
  "--meta": False, 
  "--name": "meta.runID", 
  "--outpath": None, 
  "--quality": False, 
  "--quiet": False, 
  "--tile": False, 
  "--timestamp": False, 
  "--verbose": False, 
  "--version": False, 
  "<datapath>": "/path/to/sample"
}


IGNORE_FILES = ['.DS_Store', '.Trash']

def get_subdirs(topdir):
    return [os.path.join(topdir, item) for item in os.listdir(topdir) if item not in IGNORE_FILES]

test_data = {}

test_data['MiSeq v3'] = get_subdirs('sampledata/MiSeq-samples')

test_data['HiSeq v3'] = get_subdirs('sampledata/HiSeq-samples')

#test_data['incomplete timeseries v3'] = get_subdirs('sampledata/incomplete-runs/130912_M01203_0062_000000000-A5A8N') 

test_data['HiSeq v4'] = get_subdirs('sampledata/HiSeq-v4')

for dataset_type in test_data.keys():
    print("@@@@ Starting test of %s datasets" % dataset_type)

    for subdir in test_data[dataset_type]:
        ARGS['<datapath>'] = subdir
        main(ARGS)

