from __future__ import print_function

import sys

from docopt import docopt
from .interop import InteropDataset, InteropFileNotFoundError

__doc__="""ILLUMINATE

Usage: illuminate [options] <datapath>...

NEW!!  Use --csv to dump data to CSV, headers included.

If multiple metrics selected for output, two newlines will be printed between outputs.

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

  --csv             Output results as CSV 
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
        print(msg)
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
        except Exception as e:
            dmesg('%s' % e, 1)

def run_metrics_object(InteropObject, title, to_csv=False):
    dmesg(title, 1)
    dmesg('-' * len(title), 1)

    try:
        if to_csv:
            dmesg('%s\n' % InteropObject().to_csv(), 1)
        else:
            dmesg('%s' % InteropObject(), 1)
    except InteropFileNotFoundError:
        dmesg('File not found\n', 1)

def main():
    args = docopt(__doc__, version='0.5.6')

    if args['--interactive']:
        from IPython import embed
        myDataset = InteropDataset(args['<datapath>'][0]) 
        embed()
        sys.exit()
    else:
        calculate_verbosity(args['--verbose'], args['--quiet'])
        arrange_writing_to_file(args['--dump'])

        #TODO prettify: print nicer error messages when files are missing
        #
        #TODO active_runs: forgive lack of metadata (allow read_config & flowcell_layout to be provided on CLI?)

        for datapath in args['<datapath>']:
            ID = InteropDataset(datapath)
            if args['--all'] or args['--meta']:
                run_metrics_object(ID.Metadata, "METADATA", args['--csv'])
            if args['--all'] or args['--tile']:
                run_metrics_object(ID.TileMetrics, "SUMMARY", args['--csv'])
            if args['--all'] or args['--quality']:
                run_metrics_object(ID.QualityMetrics, "QUALITY", args['--csv'])
            if args['--all'] or args['--index']:
                run_metrics_object(ID.IndexMetrics, "INDEXING", args['--csv'])
            if args['--all'] or args['--error']:
                run_metrics_object(ID.ErrorMetrics, "ERRORS", args['--csv'])
            if args['--all'] or args['--corint']:
                run_metrics_object(ID.CorrectedIntensityMetrics, "CORRECTED INTENSITY", args['--csv'])
            if args['--all'] or args['--extraction']:
                run_metrics_object(ID.ExtractionMetrics, "EXTRACTION", args['--csv'])
            if args['--all'] or args['--control']:
                run_metrics_object(ID.ControlMetrics, "CONTROL", args['--csv'])

    if OUTFILE:
        OUTFILE.close()

if __name__=='__main__':
    main()
