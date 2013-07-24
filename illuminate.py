from docopt import docopt

from illuminate import InteropDataset, print_sample_dataset

USAGE = """Usage: illuminate.py <datapath>...

  -h --help     Show this screen.
  --version     Show version.
  -q, --quiet   Suppress all console output -- use with dump-to-file option (--dump)
  -d, --dump=<out_filename>  Output parser results to file. [default: False] 

  --quality         Parse quality metrics               [default:True]
  --tile            Parse tile metrics                  [default:True]
  --index           Parse index metrics                 [default:True]
  --error           Parse error metrics                 [default:False]
  --corint          Parse corrected intensity metrics   [default:False]
  --extraction      Parse extraction metrics            [default:False]
  --image           Parse image metrics (not yet supported)

  --resequencing    Parse ResequencingRunStatistics.xml [default:False]

  --csv=<csv_filename> Output results as CSV (not yet supported)  [default:'results.csv']
"""


def calculate_verbosity(verbose, quiet):
    global VERBOSITY
    if quiet:
        VERBOSITY=0
    elif verbose and not quiet:
        VERBOSITY=2
    else:
        VERBOSITY=1
    return

if __name__=='__main__':

    args = docopt(USAGE,version='0.1')

    calculate_verbosity(args['--verbose'], args['--quiet'])

    for 
    myDataset = InteropDataset(args['<datapath>'])
    
    print_sample_dataset(myDataset)

