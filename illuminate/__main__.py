from docopt import docopt
from interop import InteropDataset

__doc__="""ILLUMINATE

Usage: illuminate [options] <datapath>...

  -h --help             Show this screen.
  --version             Show version.
  -v, --verbose         Increase verbosity           
  -q, --quiet           Suppress all console output   
  -d, --dump=<outfile>  Output parser results to file. 
  -i, --interactive     Load dataset into iPython for interactive fun.

  --all             Parse and print everything

  --meta            Print metadata
  --quality         Parse quality metrics
  --tile            Parse tile metrics
  --index           Parse index metrics
  --error           Parse error metrics
  --corint          Parse corrected intensity metrics
  --extraction      Parse extraction metrics
  --control         Parse control metrics
  --image           Parse image metrics (not yet supported)

  --csv=<csv_filename> Output results as CSV (not yet supported)
"""

#TODO: SAV_emu
"""
  --analysis        Print an emulation of the Analysis screen
  --summary         Print an emulation of the Summary screen
  --indexing        Print an emulation of the Indexing screen
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

    args = docopt(__doc__,version='0.4')

    if args['--interactive']:
        from IPython import embed
        myDataset = InteropDataset(args['<datapath>'][0]) 
        embed()
    else:
        calculate_verbosity(args['--verbose'], args['--quiet'])
        arrange_writing_to_file(args['--dump'])

        #TODO: print nicer error messages when binary file is missing

        for datapath in args['<datapath>']:
            ID = InteropDataset(datapath)
            if args['--all'] or args['--meta']:
                run_metrics_object(ID.meta, "METADATA")
            if args['--all'] or args['--tile']:
                run_metrics_object(ID.TileMetrics(), "SUMMARY")
            if args['--all'] or args['--quality']:
                run_metrics_object(ID.QualityMetrics(), "QUALITY")
            if args['--all'] or args['--index']:
                run_metrics_object(ID.IndexMetrics(), "INDEXING")
            if args['--all'] or args['--error']:
                run_metrics_object(ID.ErrorMetrics(), "ERRORS")
            if args['--all'] or args['--corint']:
                run_metrics_object(ID.CorrectedIntensityMetrics(), "INTENSITY")
            if args['--all'] or args['--extraction']:
                run_metrics_object(ID.ExtractionMetrics(), "EXTRACTION")
            if args['--all'] or args['--control']:
                run_metrics_object(ID.ControlMetrics(), "CONTROL")

        #TODO: SAV_emu
    if OUTFILE:
        OUTFILE.close()

