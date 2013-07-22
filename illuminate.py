from docopt import docopt

from illuminate import InteropDataset, print_sample_dataset


USAGE = """Usage: illuminate.py <datapath>

  -h --help     Show this screen.
  --version     Show version.
  -q, --quiet   Suppress all console output -- use with dump-to-file option (--dump)
  -d, --dump=<outfilename>  Output parser results to file. [default: False] 

  --quality         Parse quality metrics               [default:True]
  --tile            Parse tile metrics                  [default:True]
  --index           Parse index metrics                 [default:True]
  --error           Parse error metrics                 [default:False]
  --corint          Parse corrected intensity metrics   [default:False]
  --extraction      Parse extraction metrics            [default:False]
  --image           Parse image metrics (not yet supported)

  --resequencing    Parse ResequencingRunStatistics.xml [default:False]

  --verify
"""


args = docopt(USAGE,version='0.1')

myDataset = InteropDataset(args['<datapath>'])

print_sample_dataset(myDataset)

