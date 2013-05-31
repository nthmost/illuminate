#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# interop.py
#
# Library for parsing and manipulating the data in MiSeq and (soon) HiSeq output data.
#
# See USAGE_AND_STYLE.txt for intro and basic examples.
#
# March 2013
#
# by nthmost (naomi.most@invitae.com)
# with lots of help from ECO (Eric Olivares)

import time, os, subprocess   # subprocess purely for checking MIME types of files.
from xml.etree import ElementTree as ET

import pandas
from bitstring import BitString

from index_metrics import InteropIndexMetrics
from tile_metrics import InteropTileMetrics
from quality_metrics import InteropQualityMetrics


# working, but not yet integrated into InteropDataset:

from corint_metrics import InteropCorrectedIntensityMetrics 
from control_metrics import InteropControlMetrics
from extraction_metrics import InteropExtractionMetrics

from utils import dmesg

#### CONFIGURABLE THINGS
#
# THIS STUFF WILL BE MOVED INTO A MORE PYTHONIC CONFIG INI TYPE THING.
#
# Configuration of filenames, paths, and types/amounts of output logging.
# (Most people will not need to edit this stuff.)

# Name of directory containing Interop binaries. Usually "InterOp".
BINFILE_DIR_NAME = "InterOp"

#### MINIMUM VIABLE DATASETS
# 
# ...just enough XML and BIN to get what you need.
#
# These lists are used by the InteropDataset class to do a basic sanity check of the supplied data directory.

# Here are all the files available (known as of 3/8/2013)
# MVD_xml = ["CompletedJobInfo.xml", "RunInfo.xml", "runParameters.xml", "ResequencingRunStatistics.xml"]

# ...but the following 2 provide everything we really need.
MVD_xml = ["CompletedJobInfo.xml", "ResequencingRunStatistics.xml"]

# Here all the files available in binary dataset (known as of 3/8/2012)
# (quality metrics binary seems to always be QMetricsOut.bin, not QualityMetricsOut.bin as in the spec.)

# MVD_bin = ["ExtractionMetricsOut.bin", "QMetricsOut.bin", "TileMetricsOut.bin", "IndexMetrics.bin",
#       "CorrectedIntMetricsOut.bin", "ControlMetricsOut.bin", "ErrorMetricsOut.bin", "ImageMetricsOut.bin"]

# ...but at the moment, we're just using the following.
MVD_bin = ["QMetricsOut.bin", "TileMetricsOut.bin", "IndexMetricsOut.bin"]


# BINARY and XML FILEMAPs
#
# "codenames" (rather than filenames) are used internally in SeqDataset to refer to files.
# (The files themselves contain no explicit indication of what's inside them.)
#
# The FILEMAP variables contain mappings of codename to filename.
#
##
# FUTURE: use ALIASES to select file (since there are several different filenames out there).

BIN_FILEMAP = { 'extraction': "ExtractionMetricsOut.bin",
                 'quality': "QMetricsOut.bin",
                 'error': "ErrorMetricsOut.bin",
                 'tile': "TileMetricsOut.bin",
                 'correctedintensity': "CorrectedIntensityMetricsOut.bin",
                 'control': "ControlMetricsOut.bin",
                 'image': "ImageMetricsOut.bin",
                 'index': "IndexMetricsOut.bin" }

XML_FILEMAP = { 'runinfo': 'RunInfo.xml',
                'runparams': 'runParameters.xml',
                'reseqstats': 'ResequencingRunStatistics.xml',
                'completed': 'CompletedJobInfo.xml' }


##
# FUTURE: use ALIASES to select file (since there are several different filenames out there).

#BIN_ALIASES = { 'extraction': ["ExtractionMetricsOut.bin", "ExtractionMetrics.bin"],
#                'quality': ["QMetricsOut.bin", "QualityMetricsOut.bin", "QualityMetrics.bin"],
#                'error': ["ErrorMetricsOut.bin", "ErrorMetrics.bin"],
#                'tile': ["TileMetricsOut.bin", "TileMetrics.bin"],
#                'correctedintensity': ["CorrectedIntensityMetricsOut.bin", "CorrectedIntensity.bin"],
#                'control': ["ControlMetricsOut.bin", "ControlMetrics.bin"],
#                'image': ["ImageMetricsOut.bin", "ImageMetrics.bin"] 
#                'index': ["IndexMetricsOut.bin", "IndexMetrics.bin"] }}

#XML_ALIASES = { 'runinfo': ['RunInfo.xml'],
#               'runparams': ['runParameters.xml'],
#               'reseqstats': ['ResequencingRunStatistics.xml'],
#               'completed': ['CompletedJobInfo.xml'] }



#### END OF CONFIGURABLE THINGS ####

class InteropMetadata:
    "Parser for sequencer's XML files describing a single run. Supply with directory to instantiate."
    
    __version = 0.1     # version of this parser.
    
    xmldir = ""
    
    experiment_name = ""        # "RU1453:::/locus/data/run_data//1337/1453"
    investigator_name = ""      # "Locus:::Uncle_Jesse - 612 - MiSeq"
    runID = ""          # cf CompletedJobInfo.xml / RTARunInfo / Run param "Id"
    
    start_datetime = ""
    end_datetime = ""
    
    rta_run_info = { }

    # read_config: a list of dictionaries, each of which describe a single read from the sequencer.
    read_config = []
    
    # Flow cell layout: necessary to enable parsing of different machine types' binaries.
    # Defaults to MiSeq typical values.

    flowcell_layout = { 'lanecount': 1,      # cf CompletedJobInfo.xml and RunInfo.xml (redundant) 
                        'surfacecount': 2,
                        'swathcount': 1, 
                        'tilecount': 14 }
                
    # Read numbers from ResequencingRunStats.xml 
    # Example: { 'clusters_raw': 19494893, 'clusters_PF': 17381252, 'unindexed': 508055, 'unindexed_PF': 16873197, 
    #               'unaligned': 18572490, 'unaligned_PF': 16973197 }   
    resequencing_stats = {}

    def __init__(self, xmldir, AUTO=True):
        """Takes the absolute path of a sequencing run data directory as sole required variable.
           Attempts to parse CompletedJobInfo.xml (or viable alias). If not available, uses 
           runParameters.xml and/or runInfo.xml, which have some overlapping info (but not all).
           
           2nd param (boolean AUTO, default True) controls whether class attempts to parse automatically.
           Individual parsers can be explicitly called via their respective methods.
           
           Be aware that parsing methods are DESTRUCTIVE to existing instance data."""

        self.xmldir = xmldir
        
        # CompletedJobInfo.xml is the most complete XML file in the set for what we need,
        # but in a pinch we can parse RunInfo.xml for some data.
        # (runParameters.xml can be available but not really usable for several reasons.)
        
        # Getting a flowcell_layout is the top priority since it informs the binary parsers.

        if AUTO:
            try:
                self.parse_CompletedJobInfo(os.path.join(xmldir, XML_FILEMAP['completed']))
            except IOError:
                self.parse_RunInfo(os.path.join(xmldir, XML_FILEMAP['runinfo']))

            try:
                self.parse_ResequencingRunStats(os.path.join(xmldir, XML_FILEMAP['reseqstats']))
            except IOError:
                dmesg("[InteropMetadata] Warning: ResequencingRunStatistics file not found.", 2)
                

    def parse_Run_ET(self, run_ET):
        "parses chunk of XML associated with the RTA Run Info blocks in (at least) 2 xml files."

        self.rta_run_info = { 'instrument': run_ET.find("Instrument").text,     # M00612
                              'flowcell': run_ET.find("Flowcell").text,         # 000000000-A316T
                              'date': run_ET.find("Date").text }                # 130208
    
        flowcell_ET = run_ET.find("FlowcellLayout")
        self.flowcell_layout = { 'lanecount': int(flowcell_ET.attrib['LaneCount']),
                        'surfacecount': int(flowcell_ET.attrib['SurfaceCount']),
                        'swathcount': int(flowcell_ET.attrib['SwathCount']),
                        'tilecount': int(flowcell_ET.attrib['TileCount']) }     
        
        # Run / Reads - describes number of cycles per read (and if read is an Index) in sequencing run.
        
        # Because parsing is understood to be destructive, and Reads can be found in multiple files,
        # we start by emptying out whatever's currently in the read_config array for this instance.
        
        self.read_config = []
        read_num = 0
        for item in run_ET.find("Reads"):
            read_num += 1       # redundant safety assignment to read_num
            self.read_config.append( {'read_num': read_num,
                                      'cycles': int(item.attrib['NumCycles']), 
                                      'is_index': True if item.attrib["IsIndexedRead"]=="Y" else False } )      
    
    
    
    def parse_ResequencingRunStats(self, filepath):
        "parses ResequencingRunStatistics.xml (or viable alias) to fill instance variables."
        
        tree = ET.parse(filepath)
        root = tree.getroot()   # should be "StatisticsResequencing"
        runstats_ET = root.find("RunStats")
        
        self.resequencing_stats = { 'clusters_raw': int(runstats_ET.find("NumberOfClustersRaw").text),
                                    'clusters_pf': int(runstats_ET.find("NumberOfClustersPF").text),
                                    'unindexed': int(runstats_ET.find("NumberOfUnindexedClusters").text),
                                    'unindexed_pf': int(runstats_ET.find("NumberOfUnindexedClustersPF").text),
                                    'unaligned': int(runstats_ET.find("NumberOfUnalignedClusters").text),
                                    'unaligned_pf': int(runstats_ET.find("NumberOfUnalignedClustersPF").text),
                                    'duplicate': int(runstats_ET.find("NumberOfDuplicateClusters").text) }

    def parse_CompletedJobInfo(self, filepath):
        "parses CompletedJobInfo.xml (or viable alias) to fill instance variables."
        # comments show example data from a real MiSeq run (2013/02)
        
        tree = ET.parse(filepath)
        root = tree.getroot()       #should be "AnalysisJobInfo"
    
        # Something to be aware of: RTARunInfo contains a "version" attribute.
        # (This parser knows how to deal with version 2.)
        self.rta_version = root.find("RTARunInfo").attrib['Version']

        # original location of data output from the sequencer.
        self.output_folder = root.find("RTAOutputFolder").text 
        
        # TODO: reformat these dates into something nicer (more useable).
        self.start_datetime = root.find("StartTime").text           # 2013-02-09T15:51:50.0811937-08:00
        self.end_datetime = root.find("CompletionTime").text        # 2013-02-09T16:06:44.0124452-08:00
        
        # dechunk all of the major sections we want to extract data from.
        sheet_ET = root.find("Sheet")
        header_ET = sheet_ET.find("Header")
        run_ET = root.find("RTARunInfo").find("Run")
        
        # Sheet / *
        try:
            self.runtype = sheet_ET.find("Type").text       # MiSeq, HiSeq, etc.
        except AttributeError:
            #older (early 2012) XML files have no "Type" token.
            self.runtype = ""
                
        # Sheet / Header / *
        self.investigator_name = header_ET.find("InvestigatorName").text
        self.project_name = header_ET.find("ProjectName").text
        self.experiment_name = header_ET.find("ExperimentName").text

        # RTARunInfo / Run / *          
        self.runID = run_ET.attrib["Id"]                        # 130208_M00612_0046_000000000-A316T

        self.parse_Run_ET(run_ET)

        # excerpt from CompletedJobInfo.xml / RTARunInfo Version 2
        """<RTARunInfo Version="2">
        <Run Id="130208_M00612_0046_000000000-A316T">
          <Flowcell>000000000-A316T</Flowcell>
          <Instrument>M00612</Instrument>
          <Date>130208</Date>
          <Reads>
            <Read NumCycles="151" IsIndexedRead="N" />
            <Read NumCycles="6" IsIndexedRead="Y" />
            <Read NumCycles="151" IsIndexedRead="N" />
          </Reads>
          <FlowcellLayout LaneCount="1" SurfaceCount="2" SwathCount="1" TileCount="14" />
          <AlignToPhiX />
        </Run>
        </RTARunInfo>"""


    def parse_RunParameters(self, filepath):
        "partially implemented / not used.  (No FlowcellLayout in this file.)"
        tree = ET.parse(filepath)
        root = tree.getroot()

        self.runID = root.find("RunID").text
        
        # TODO: normalize this variable
        self.start_datetime = root.find("RunStartDate").text    # format: 130208 YYMMDD
        
        for item in root.find("Reads"):
            #Different format from that in CompletedJobInfo.xml (contains read Number)
            self.read_config.append( {'read_num': int(item.attrib['Number']),
                                      'cycles': int(item.attrib['NumCycles']), 
                                      'is_index': True if item.attrib["IsIndexedRead"]=="Y" else False } )


    def parse_RunInfo(self, filepath):
        "parses Reads, Date, Flowcell, Instrument out of runInfo.xml -- FlowcellLayout seems to be unreliable (!?)"
        tree = ET.parse(filepath)
        run_ET = tree.getroot().find("Run")     #nothing of use in this file except <Run> subelement. 
        
        self.runID = run_ET.attrib['Id']
        
        #? is this useful information? if so, what for?  (It's not in CompletedJobInfo.xml)
        #self.runNumber = run_ET.attrib['Number']    
        
        self.rta_run_info = self.parse_Run_ET(run_ET)
        
        # Notice how FlowcellLayout in RunInfo.xml doesn't match that of CompletedJobInfo.xml (latter is correct).
        
        """<?xml version="1.0"?>
        <RunInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Version="2">
          <Run Id="120322_M00169_0027_AMS0005813-00300" Number="26">
            <Flowcell>000000000-A0GA6</Flowcell>
            <Instrument>M00169</Instrument>
            <Date>120322</Date>
            <Reads>
                <Read NumCycles="151" Number="1" IsIndexedRead="N" />
                <Read NumCycles="6" Number="2" IsIndexedRead="Y" />
                <Read NumCycles="151" Number="3" IsIndexedRead="N" />
            </Reads>
            <FlowcellLayout LaneCount="1" SurfaceCount="1" SwathCount="1" TileCount="12" />
          </Run>
        </RunInfo>"""
        

class InteropDatasetIncompleteError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InteropDatasetError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


# used by MIME type checker
FILETYPE_MIME_MAP = { 'bin': 'application/octet-stream; charset=binary\n',
                      'xml': 'application/xml; charset=us-ascii\n' }

class InteropDataset:
    """Encapsulates the physical files related to this sequencing run. 
       Performs (superficial) checks for dataset completeness.
       Absolves other classes of having to know about files and directories.
       Raises custom errors: InteropDatasetIncompleteError InteropDatasetError"""
    
    directory = ""  # supplied directory name to instantiate class (relative path)
    fullpath = ""   # calculated absolute filesystem path after instantiation
    xmldir = ""     # typically equivalent to fullpath
    bindir = ""     # typically = fullpath/Interop/

    meta = None

    def __init__(self, targetdir, CHECK_INTEGRITY=False):
        """Supply a path (directory) that should contain XML files, with an InterOp directory within it.
        Supply True for second parameter to do a basic dataset integrity/existence check."""

        self.directory = targetdir

        self.xmldir = self.directory
        self.bindir = os.path.join(self.directory, BINFILE_DIR_NAME)
        
        self.meta = self.Metadata()
    
        if CHECK_INTEGRITY:
            self.check_integrity()

        # holders for the parser objects. Reference via *Metrics() classes.
        self._quality_metrics = None
        self._tile_metrics = None
        self._index_metrics = None
        
        # aggregate results of parsing one or more XML files
        meta = None

    def get_binary_path(self, codename):
        "returns absolute path to binary file represented by data 'codename'"
        return os.path.join(self.bindir, BIN_FILEMAP[codename])
    
    def get_xml_path(self, codename):
        "returns absolute path to XML file represented by data 'codename'"
        return os.path.join(self.xmldir, XML_FILEMAP[codename])
    
    def Metadata(self, reload=False):
        "returns InteropMetadata class generated from this dataset's XML files"
        if self.meta == None or reload == True:
            self.meta = InteropMetadata(self.xmldir)
        return self.meta
    
    # BINARY EXTRACTION METHODS
    # Abstractions for the data files so we don't have to hard-code any filenames.
    # Make sure to keep the BIN_FILEMAP (above) up to date.
    
    # convention: InterCaps() returns associated object. thing_metrics() returns bitstring from binary.
    def QualityMetrics(self, reload=False):
        "Returns InteropQualityMetrics object from the 'quality' binary in this dataset."
        if self._quality_metrics == None or reload == True:
            self._quality_metrics = InteropQualityMetrics(self.get_binary_path('quality'), 
                                    flowcell_layout = self.meta.flowcell_layout,
                                    read_config = self.meta.read_config )
        return self._quality_metrics
        
    def TileMetrics(self, reload=False):
        "Returns InteropTileMetrics object from the 'tile' binary in this dataset."
        if self._tile_metrics == None or reload == True:
            self._tile_metrics = InteropTileMetrics(self.get_binary_path('tile'), 
                                    flowcell_layout=self.meta.flowcell_layout,
                                    read_config=self.meta.read_config )
        return self._tile_metrics

    def IndexMetrics(self, reload=False):
        "Returns InteropIndexMetrics object from the 'index' binary in this dataset."
        if self._index_metrics == None or reload == True:
            self._index_metrics = InteropIndexMetrics(self.get_binary_path('index'), 
                                    flowcell_layout=self.meta.flowcell_layout,
                                    read_config=self.meta.read_config )
        return self._index_metrics

    # The following haven't been implemented as parsers yet.
    def extraction_metrics(self):
        "returns bitstream object from the 'extraction' binary in this dataset"
        return BitString(bytes=open(self.get_binary_path('extraction'), 'rb').read())

    def correctedintensity_metrics(self):
        "returns bitstream object from the 'correctedintensity' binary in this dataset"
        return BitString(bytes=open(self.get_binary_path('correctedintensity'), 'rb').read())

    def control_metrics(self):
        "returns bitstream object from the 'control_metrics' binary in this dataset"
        return BitString(bytes=open(self.get_binary_path('control'), 'rb').read())

    def image_metrics(self):
        "returns bitstream object from the 'image_metrics' binary in this dataset"
        return BitString(bytes=open(self.get_binary_path('image'), 'rb').read())
    
    def error_metrics(self):
        "returns bitstream object from the 'error' binary in this dataset"
        return BitString(bytes=open(self.get_binary_path('error'), 'rb').read())
        
    # XML FILEHANDLE METHODS (not currently used for anything...)
    def runInfo(self):
        return open(get_xml_path('runinfo'))

    def runParameters(self):
        return open(get_xml_path('runparams'))
        
    def completedInfo(self):
        return open(get_xml_path('completed'))
        
    def reseqStats(self):
        return open(get_xml_path('reseqstats'))


    # DATA INTEGRITY CHECKING
    # Pretty basic at the moment: just checking existence and MIME type of each file.
    
    def check_file(self, filename, filetype):
        "Basic MIME type check using the POSIX 'file' command."
        
        if filetype=="xml":
            filepath = os.path.join(self.xmldir, filename)
        elif filetype=="bin":
            filepath = os.path.join(self.bindir, filename)
        else:
            raise InteropDatasetError("We don't like this type around here: %s. These are the types we like: xml bin" % filetype)
        
        res = subprocess.check_output(['file', '-b', '--mime', filepath ])
        if res == FILETYPE_MIME_MAP[filetype]:
            return True
        elif "No such file or directory" in res:
            #this should logically never happen, actually.
            raise InteropDatasetError("That's weird, the file command says %s doesn't exist." % filepath )
        else:
            raise InteropDatasetError("Filename / MIME type mismatch: %s (%s)" % (filename, filetype), 1)
   
    def check_integrity(self):
        "checks for a complete set of binary and xml files to define a sequencing run."
        xmlfiles = os.listdir(self.xmldir)
        for item in MVD_xml:
            if item not in xmlfiles:
                raise InteropDatasetIncompleteError("%s wasn't found among XML files" % item)
            else:
                self.check_file(item, 'xml')
        
        binfiles = os.listdir(self.bindir)
        for item in MVD_bin:                # (filename.lower() for filename in MVD_bin):
            if item not in binfiles:
                #TODO: place item in a list, continue iterating, then raise following error with list instead.
                raise InteropDatasetIncompleteError("%s wasn't found among binaries" % item)
            else:
                self.check_file(item, 'bin')

def print_sample_dataset(dirname):
    one = InteropDataset(dirname, True)
    
    meta = one.Metadata()
    
    print "Resequencing Statistics:" 
    print meta.resequencing_stats
    print ""
    
    print "Flowcell Layout:"
    print meta.flowcell_layout
    print ""
    
    print "Read Configuration:"
    print meta.read_config
    print ""
    
    tm = one.TileMetrics()
    print "Tile Metrics:"
    print tm.to_dict()
    print ""
    
    print "Quality Metrics (% >= Q30 per read):"
    qm = one.QualityMetrics()
    for read in meta.read_config:
        print "Read %i: %f %s" % (read['read_num'], qm.get_qscore_percentage(30, read['read_num']-1),
                                    "(Index)" if read['is_index'] else "")                        
    print ""

    print "Index Metrics (sum of PF clusters per index):"
    im = one.IndexMetrics()
    #print im.df
    print im.to_dict()
    print ""
    
    print "IndexMetrics + TileMetrics = SAV INDEXING tab"
    print ""
    print "Total Reads: %i" % tm.num_clusters
    print "Reads PF: %i" % tm.num_clusters_pf
    print "Percentage Reads Identified (PF): %f" % (float(im.total_ix_reads_pf / tm.num_clusters_pf)*100)
    print ""
    print im.pivot
    
    #import ipdb; ipdb.set_trace()



if __name__=='__main__':
    import sys

    try:
        dirname = sys.argv[1] 
    except IndexError:
        print "Supply the absolute or relative path to a directory of sequencing rundata."
        print "Example:  python generate.py /home/username/seqruns/2013-02/0"
        sys.exit()
        
    print_sample_dataset(dirname)
    
    
    
    