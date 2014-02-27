from __future__ import print_function

import os, sys, time

from docopt import docopt
from .interop import InteropDataset 
from .exceptions import InteropFileNotFoundError

__doc__="""ILLUMINATE

Usage: illuminate [options] <datapath>...
       illuminate [options] [--csv | --json] <datapath>...

By default, illuminate prints a summary of most commonly desired characteristics rather
than raw data (e.g. cluster density from --tile, Q30 percentage scores from --quality.)

Raw data can be output to --csv or --json, either to STDOUT or to file(s). If no --outfile
specified, data will be sent to STDOUT with two newlines separating each metric section.

The --outfile / -o param forms the basis of the filename and may include a directory path.

For example, 

  illuminate --csv --quality --extraction -o /data/dump/metrics.csv /path/to/dataset 

produces:  /data/dump/quality.metrics.csv, /data/dump/extraction.metrics.csv

This utility is undergoing rapid development; please treat as Very Beta. --NM 2/21/2014

  -h --help             Show this screen.
  --version             Show version.
  -v, --verbose         Increase verbosity           
  -q, --quiet           Suppress all console output   
  -d, --debug           Increase verbosity and prefix output with Unix timestamps. 
  -i, --interactive     Load dataset into iPython for interactive fun.
  -o, --outfile=outfile Output parser results to file (please read docs). [default: '']

  --all             Parse and print everything
  --meta            Print flowcell_layout and read_config

PARSING OPTIONS:
  --quality         Parse quality metrics 
  --tile            Parse tile metrics
  --index           Parse index metrics
  --error           Parse error metrics
  --corint          Parse corrected intensity metrics
  --extraction      Parse extraction metrics
  --control         Parse control metrics

DATA DUMP FORMATS:
  --csv             Output raw data from parser as CSV 
  --json            Output raw data from parser as JSON (not yet implemented).
"""

#TODO: smarter_filenames
"""
  --timestamp       Generate filename containing Unix timestamp.
  --makedirs        Create a unique directory for each dataset (use in combo with -o).
"""

#TODO: SAV_emu
"""
  --analysis        Produce an emulation of the Analysis screen
  --summary         Produce an emulation of the Summary screen
  --indexing        Produce an emulation of the Indexing screen
  --image           Parse image metrics (no plans to support)
"""

VERBOSITY = 1
DEBUG = False

def dmesg(msg, lvl=1):
    if DEBUG: msg = '[DEBUG][%f] %r' % (time.time(), msg)
    if VERBOSITY >= lvl:
        print(msg)

def construct_filename(codename, args):
    #TODO: smarter_filenames

    if args['--json']:
        suffix = 'json'
    else:
        suffix = 'csv'

    outpath = ''
    if args['--outfile']=='':
        # if no filename or directory specified, make one in CWD.
        outpath = '%s.%s.%s' % (codename, time.time(), suffix)

    elif os.path.isdir(args['--outfile']):
        # check if --outfile is a directory. If so, assume user intended to dump
        # to this directory (instead of assuming that, for example, "/opt/data" 
        # means the user intends to create a file called /opt/codename.data )
        outpath = os.path.join(args['--outfile'], '%s.dump.%s' % (codename, suffix))

    else:
        dirname, fnamebase = os.path.split(args['--outfile'])
        if dirname and fnamebase=='':
            fnamebase = 'dump.%s' % (suffix)
        outpath = os.path.join(dirname, '%s.%s' % (codename, fnamebase))

    print(outpath)
    return outpath

def write_data(output, codename, args):
    if args['--outfile']:
        outpath = construct_filename(codename, args)
        datafile = open(outpath, 'wb')
        try:
            datafile.write(output+'\n')
        except Exception as e:
            dmesg('Error writing to file: %r' % e, 0)
        datafile.close()
    else:
        print(output)

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
        if args['--csv'] or args['--json']:
            dump(InteropObject, args)
        else:
            dmesg(title, 1)
            dmesg('-' * len(title), 1)
            dmesg('%s' % InteropObject(), 1)
    except InteropFileNotFoundError:
        dmesg('%s: File not found\n' % title, 1)

    dmesg('%s: finished' % title, 2)


def dump(InteropObject, args):
    try:
        metricobj = InteropObject()
        if args['--csv']:
            write_data(metricobj.to_csv(), metricobj.codename, args)
        elif args['--json']:
            write_data(metricobj.to_json(), metricobj.codename, args)

    except AttributeError:
        dmesg('Metadata has no CSV or JSON output.\n', 2)


def main():
    args = docopt(__doc__, version='0.5.7')
    print(args)

    if args['--interactive']:
        from IPython import embed
        myDataset = InteropDataset(args['<datapath>'][0]) 
        embed()
        sys.exit()
    else:
        calculate_verbosity(args)

        for datapath in args['<datapath>']:
            ID = InteropDataset(datapath)
            if args['--all'] or args['--meta']:
                run_metrics_object(ID.Metadata, "METADATA", args)
            if args['--all'] or args['--tile']:
                run_metrics_object(ID.TileMetrics, "TILE METRICS", args)
            if args['--all'] or args['--quality']:
                run_metrics_object(ID.QualityMetrics, "QUALITY METRICS", args)
            if args['--all'] or args['--index']:
                run_metrics_object(ID.IndexMetrics, "INDEXING METRICS", args)
            if args['--all'] or args['--error']:
                run_metrics_object(ID.ErrorMetrics, "ERROR METRICS", args)
            if args['--all'] or args['--corint']:
                run_metrics_object(ID.CorrectedIntensityMetrics, "CORRECTED INTENSITY", args)
            if args['--all'] or args['--extraction']:
                run_metrics_object(ID.ExtractionMetrics, "EXTRACTION METRICS", args)
            if args['--all'] or args['--control']:
                run_metrics_object(ID.ControlMetrics, "CONTROL METRICS", args)

if __name__=='__main__':
    main()
