#!/usr/bin/env python
#
# interopspider.py
#
# March 1, 2013
# by nthmost (naomi.most@invitae.com)
#
# This script grabs InterOp output binaries and puts them into subdirectories
# of the current working directory.
#
# MINIMUM VIABLE DATASET for viewing in Illumina SAV:
# - all XML files in level2 subdir (see below for definition)
# - the entire InterOp directory
#
# USAGE: ./interop-spider.py monthname
# 
# * run without arguments to see all subdirectories available in the archive.
# * configure the output directory by setting DEST_DIR_ROOT below.
# *  

import os
import sys
import time

from docopt import docopt

DEFAULTS = {'destdir': "."} 

__doc__="""Seqrun Spider

This script acquires the minimum viable datasets necessary to extract metrics from
MiSeq and HiSeq runs (namely, the XML files and the InterOp directory).

The first argument must be the root directory to source runs from.

The second argument will be the run directories themselves.

Supply as many subdirectories as you like. 

"*" is a valid argument (retrieve all subdirectories of the root location).

Usage:
  seqrun_spider.py [options] <rootdir> <rundirs>...
  seqrun_spider.py [options] <rootdir> *

  -h --help                         Show this screen.
  --version                         Show version.
  -o --outputdir=<%(destdir)s>        Directory to store copied files.
  -v --verbose                      Print a few more status messages to stdout.
  -d --debug                        Include a lot more information in output (cumulative with --verbose).
  -q --quiet                        Suppress all messages (except for fatal errors) (overrides -d and -v).
""".format(DEFAULTS)

VERBOSITY = 1
DEBUG = False

# In case you need to modify how the copy and mark commands function.
#
# (The "mark" command serves to retain the information about what the name of the
# directory that the dataset came from was named.)

COPY_CMD = "cp %s %s"
RCOPY_CMD = "cp -r %s %s"
MARK_CMD = "touch %s"

# IGNORE_LIST: Any extraneous stuff that might appear in the subdirectories.
IGNORE_LIST = ['.DS_Store']

# No Configuration Needed Beyond This Point (here there be dragons, etc).

def dmesg(msg, lvl=1):
    msg = "[%f] " % time.time() + msg
    if VERBOSITY >= lvl:
        print msg

def do_command(cmd):
    dmesg("%s" % cmd, 3)
    if not DEBUG: os.popen(cmd)
    dmesg("Completed %s" % cmd, 4)

def create_dir(name):
    dmesg ("mkdir %s" % name, 3)
    try:
        if not DEBUG: os.mkdir(name)
    except OSError:
        dmesg("Directory %s already existed." % name, 4)
        pass  #that's fine if it already exists.

def mark_dir(code, directory):
    "Makes a blank file with the name of the rundata directory from whence it came."
    make_mark = MARK_CMD % (os.path.join(directory, code))
    do_command(make_mark)

def get_MVDataset(abspath, args):
    """   
       * copy the InterOp subdirectory of targetdir to new directory under args['<outputdir>']
       * use the name of the source directory to "mark" the newly created folder (see MARK_CMD).
    """

    simple_timestamp = str(time.time()).split('.')[0]
    print abspath
    sourcedirname = os.path.split(os.path.split(abspath)[0])

    dmesg("DATASET: %s" % sourcedirname, 1)

    destdir = os.path.join(args['<outputdir>'], sourcedirname)
    create_dir(destdir)
    create_dir(os.path.join(destdir, simple_timestamp))

    # copy "InterOp" directory as a whole.
    copy_interop = RCOPY_CMD % (os.path.join(abspath,"InterOp"), destdir)

    # copy all XML files found in copydir
    copy_xml = COPY_CMD % (os.path.join(abspath,"*.xml"), destdir)
        
    mark_dir(sourcedirname, os.path.join(destdir))

    do_command(copy_interop)
    do_command(copy_xml)


def available_rundirs(targetdir):
    try:
        return os.listdir(targetdir)
    except OSError:
        print "\n!!!"
        print "Oops, couldn't read from %s" % targetdir
        print ""
        print "(Maybe you need to mount your data directory?)"
        sys.exit()

def set_verbosity(args):
    global VERBOSITY
    global DEBUG
    if args['--debug']:
        VERBOSITY = 3
        DEBUG = True

    if args['--verbose']:
        VERBOSITY += 1

    if args['--quiet']:
        VERBOSITY = -1


def get_abspath(rootdir, subdir):
    abspath = os.path.join(rootdir, subdir)
    if os.path.exists(abspath):
        return abspath
    else:
        dmesg("Skipping %s -- not a valid directory to source files from." % abspath, 1)

def main(args):
    rundirs = []
    abspath_list = []
    set_verbosity(args)

    rootdir = args['<rootdir>']
    if args['<rundirs>'] == ['*']:
        rundirs = os.listdir(rootdir)
    else:
        rundirs = args['<rundirs>']

    for item in rundirs:
        if item in IGNORE_LIST:
            continue
        abspath_list.append(get_abspath(rootdir, item))

    for abspath in abspath_list:
        get_MVDataset(abspath, args)

if __name__=='__main__':
    args = docopt(__doc__, version=0.1)
    main(args)

