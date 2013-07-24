from docopt import docopt
from interop import InteropDataset

__doc__="""Usage: illuminate.py [options] <datapath>...

  -h --help             Show this screen.
  --version             Show version.
  -v, --verbose         Increase verbosity           
  -q, --quiet           Suppress all console output   
  -d, --dump=<outfile>  Output parser results to file. 

  --meta            Parse metadata                      [default: True]
  --quality         Parse quality metrics               [default: True]
  --tile            Parse tile metrics                  [default: True]
  --index           Parse index metrics                 [default: True]
  --error           Parse error metrics                 [default: False]
  --corint          Parse corrected intensity metrics   [default: False]
  --extraction      Parse extraction metrics            [default: False]
  --control         Parse control metrics               [default: False]
  --image           Parse image metrics (not yet supported)

  --csv=<csv_filename> Output results as CSV (not yet supported)  [default:'results.csv']
"""

VERBOSITY = 1
DEBUG = False
OUTFILE = None

def dmesg(msg, lvl=1):
    #msg = '[%f] ' % time.time() + msg
    if DEBUG: msg = '[DEBUG] ' + msg
    if VERBOSITY >= lvl:
        print msg
    if OUTFILE:
        OUTFILE.write(msg+'\n')
        OUTFILE.flush()

def calculate_verbosity(verbose, quiet):
    global VERBOSITY
    if quiet:
        VERBOSITY=0
    elif verbose and not quiet:
        VERBOSITY=2
    else:
        VERBOSITY=1

def arrange_writing_to_file(filename):
    global OUTFILE
    if filename:
        try:
            OUTFILE = open(filename, 'w')
        except Exception, e:
            dmesg('%s' % e, 1)

def run_metrics_object(InteropObject, title):
    dmesg(title, 1)
    dmesg('-' * len(title), 1)
    dmesg('%s' % InteropObject, 1)

if __name__=='__main__':

    args = docopt(__doc__,version='0.1')
    calculate_verbosity(args['--verbose'], args['--quiet'])
    arrange_writing_to_file(args['--dump'])

    for datapath in args['<datapath>']:
        ID = InteropDataset(datapath)
        if args['--meta']:
            run_metrics_object(ID.meta, "METADATA")
        if args['--tile']:
            run_metrics_object(ID.TileMetrics(), "SUMMARY")
        if args['--quality']:
            run_metrics_object(ID.QualityMetrics(), "QUALITY")
        if args['--index']:
            run_metrics_object(ID.IndexMetrics(), "INDEXING")
        if args['--error']:
            run_metrics_object(ID.ErrorMetrics(), "ERRORS")
        if args['--corint']:
            run_metrics_object(ID.CorrectedIntensityMetrics(), "INTENSITY")
        if args['--extraction']:
            run_metrics_object(ID.ExtractionMetrics(), "EXTRACTION")
        if args['--control']:
            run_metrics_object(ID.ControlMetrics(), "CONTROL")

    if OUTFILE:
        OUTFILE.close()
