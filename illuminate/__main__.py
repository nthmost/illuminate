from __future__ import print_function

import os, sys, time

from docopt import docopt
from .interop import InteropDataset 
from .exceptions import InteropFileNotFoundError

__doc__="""ILLUMINATE

Usage: illuminate [options] <datapath>
       illuminate [options] [--csv | --json] <datapath>

By default, illuminate prints a summary of most commonly desired characteristics rather
than raw data (e.g. cluster density from --tile, Q30 percentage scores from --quality.)

Raw data can be output to --csv or --json, either to STDOUT or to file(s). If no --outpath
specified, data will be sent to STDOUT with two newlines separating each metric section.

The --outpath / -o param should contain an already existing directory which the user has
permissions to create new directories within.

For example, 

  illuminate --csv --quality --extraction -o /data/dump/ /path/to/dataset 

produces:  /data/dump/name/quality.metrics.csv, /data/dump/name/extraction.metrics.csv

...where `name` is either a user-supplied --name parameter or the RunID given by the 
sequencer (as recorded in RTA_Run_Info).

This utility is undergoing rapid development; please treat as Very Beta. --NM 2/21/2014

  -h --help             Show this screen.
  --version             Show version.
  -v, --verbose         Increase verbosity           
  -q, --quiet           Suppress all console output   
  -d, --debug           Increase verbosity and prefix output with Unix timestamps. 
  -i, --interactive     Load dataset into iPython for interactive fun.
  -n --name=name        Set a name for this dataset. [default: meta.runID]
  
  --all             Parse and print (or dump) everything
  --meta            Print flowcell_layout and read_config

  --tile            Parse tile metrics
  --quality         Parse quality metrics 
  --index           Parse index metrics
  --error           Parse error metrics
  --corint          Parse corrected intensity metrics
  --extraction      Parse extraction metrics
  --control         Parse control metrics

  --csv             Output raw data from parser as CSV 
  --json            Output raw data from parser as JSON
  
  -o, --outpath=<outpath> Output parser results to directory
  -t, --timestamp   Generate filename(s) containing Unix timestamps (format: timestamp.metric.format)
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

DEFAULT_FNAME = '%s.%s'  #codename, suffix
TIMESTAMP_FNAME = '%i.%s.%s'   # timestamp, codename, suffix

def timestamp():
    return time.time()

def dmesg(msg, lvl=1):
    if DEBUG: msg = '[DEBUG][%f] %r' % (timestamp(), msg)
    if VERBOSITY >= lvl:
        print(msg)

def check_output_basedir(loc):
    if not os.path.exists(loc):
        dmesg("Fatal: --outpath '%s' does not exist." % loc, 1)
        sys.exit()

    if os.path.isdir(loc):
        if os.access(loc, os.W_OK):
            return loc
        else:
            dmesg('Fatal: cannot write to %s (check permissions)' % loc, 1)
            sys.exit()
    else:
        dmesg('Fatal: %s exists but is not a directory.' % loc, 1)
        sys.exit()

def construct_filename(codename, args):
    if args['--json']:
        suffix = 'json'
    else:
        suffix = 'csv'

    outdir = os.path.join(check_output_basedir(args['--outpath']), args['--name'])
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    if args['--timestamp']:
        filename = TIMESTAMP_FNAME % (args['--timestamp'], codename, suffix)
    else:
        filename = DEFAULT_FNAME % (codename, suffix)
    return os.path.join(outdir, filename)

def write_data(output, codename, args):
    if args['--outpath']:
        outpath = construct_filename(codename, args)
        datafile = open(outpath, 'wb')
        try:
            datafile.write(output+'\n')
            dmesg('wrote %s' % outpath, 1)
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

def print_meta(metaobj, args):
    dmesg('Name:   %s' % args['--name'], 1)
    dmesg('Run ID: %s' % metaobj.runID, 1)
    dmesg('%s\n' % metaobj, 1)

def main():
    args = docopt(__doc__, version='0.5.7')

    if args['--interactive']:
        from IPython import embed
        myDataset = InteropDataset(args['<datapath>']) 
        embed()
        sys.exit()
    else:
        calculate_verbosity(args)

        try:
            ID = InteropDataset(args['<datapath>'])
        except IOError, e:
            dmesg(e, 1)
            sys.exit()

        if args['--name']=='meta.runID':
            args['--name'] = ID.meta.runID

        if args['--all'] or args['--meta']:
            print_meta(ID.meta, args)
            
        if args['--timestamp']:
            args['--timestamp'] = timestamp()

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
