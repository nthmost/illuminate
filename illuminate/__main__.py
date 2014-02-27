from __future__ import print_function

import sys

from docopt import docopt
from .interop import InteropDataset 
from .exceptions import InteropFileNotFoundError

__doc__="""ILLUMINATE

Usage: illuminate [options] <datapath>...

       illuminate [options] dump [--csv | --json] <datapath>...

By default, illuminate prints a summary of most commonly desired characteristics rather
than raw data (e.g. cluster density from --tile, Q30 percentage scores from --quality.)

NEW in 0.5.6: The `dump` command.

Raw data can be output to --csv (and soon --json), either to STDOUT or to file(s). If no
--outfile specified, data will be sent to STDOUT with two newlines separating each metric 
section.

If multiple metrics selected, multiple files will be created using "outfile" as the basis.

For example, 

  illuminate dump --csv --tile --quality --extraction -o metrics.csv /path/to/dataset 

produces: metrics.csv.tile, metrics.csv.quality, metrics.csv.extraction

This utility is undergoing rapid development; please treat as Very Beta. --NM 2/21/2014

  -h --help             Show this screen.
  --version             Show version.
  -v, --verbose         Increase verbosity           
  -q, --quiet           Suppress all console output   
  -d, --debug           Increase verbosity and prefix output with Unix timestamps. 
  -i, --interactive     Load dataset into iPython for interactive fun.
  -o, --outfile=<outfile>  Output parser results to file. 

  --all             Parse and print everything

  --meta            Print flowcell_layout and read_config
  --quality         Parse quality metrics
  --tile            Parse tile metrics
  --index           Parse index metrics
  --error           Parse error metrics
  --corint          Parse corrected intensity metrics
  --extraction      Parse extraction metrics
  --control         Parse control metrics
  --image           Parse image metrics (not yet supported)

  --csv             Output raw data from parser as CSV 
  --json            Output raw data from parser as JSON (not yet implemented).
"""

#TODO: SAV_emu
"""
  --analysis        Produce an emulation of the Analysis screen
  --summary         Produce an emulation of the Summary screen
  --indexing        Produce an emulation of the Indexing screen
"""

VERBOSITY = 1
DEBUG = False

def dmesg(msg, lvl=1):
    if DEBUG: msg = '[DEBUG][%f] %r' % (time.time(), msg)
    if VERBOSITY >= lvl:
        print(msg)

def write_data(output, args):
    filename = args['--outfile']
    datafile = open(filename, 'wb')
    try:
        datafile.write(item+'\n')
    except Exception as e:
        dmesg('Error writing to file: %r' % e, 0)
    datafile.close()

def calculate_verbosity(args):
    global VERBOSITY
    if args['--quiet']:
        VERBOSITY=0
        return

    if args['--verbose'] or args['--debug']: 
        VERBOSITY += 1

def run_metrics_object(InteropObject, title, args):
    dmesg('%s: running' % title, 2)
    try:
        if args['--csv']:
            write_data('%s\n' % InteropObject().to_csv(), args)
        dmesg(title, 1)
        dmesg('-' * len(title), 1)
        dmesg('%s' % InteropObject(), 1)
    except InteropFileNotFoundError:
        dmesg('File not found\n', 1)
    except AttributeError:
        dmesg('Metadata has no CSV output.\n', 1)

    dmesg('%s: finished' % title, 2)


def dump(InteropObject, args):
    #TODO: this.
    dmesg('%s: running' % title, 2)

    dmesg('%s: finished' % title, 2)


def main():
    args = docopt(__doc__, version='0.5.6')

    print(args)

    if args['--interactive']:
        from IPython import embed
        myDataset = InteropDataset(args['<datapath>'][0]) 
        embed()
        sys.exit()
    else:
        calculate_verbosity(args)           #args['--verbose'], args['--quiet'])

        #TODO prettify: print nicer error messages when files are missing
        #
        #TODO active_runs: forgive lack of metadata (allow read_config & flowcell_layout to be provided on CLI?)

        for datapath in args['<datapath>']:
            ID = InteropDataset(datapath)
            if args['--all'] or args['--meta']:
                run_metrics_object(ID.Metadata, "METADATA", args)
            if args['--all'] or args['--tile']:
                run_metrics_object(ID.TileMetrics, "SUMMARY", args)
            if args['--all'] or args['--quality']:
                run_metrics_object(ID.QualityMetrics, "QUALITY", args)
            if args['--all'] or args['--index']:
                run_metrics_object(ID.IndexMetrics, "INDEXING", args)
            if args['--all'] or args['--error']:
                run_metrics_object(ID.ErrorMetrics, "ERRORS", args)
            if args['--all'] or args['--corint']:
                run_metrics_object(ID.CorrectedIntensityMetrics, "CORRECTED INTENSITY", args)
            if args['--all'] or args['--extraction']:
                run_metrics_object(ID.ExtractionMetrics, "EXTRACTION", args)
            if args['--all'] or args['--control']:
                run_metrics_object(ID.ControlMetrics, "CONTROL", args)

if __name__=='__main__':
    main()
