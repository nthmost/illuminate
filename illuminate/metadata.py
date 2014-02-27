#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# InteropDataset
# Library encapsulating the XML and bin files from MiSeq and HiSeq output.
#
# InteropMetadata
# Parser for XML files from MiSeq / HiSeq run data.
#
# See README for intro and basic examples.
#
# March 2013
# by nthmost (naomi.most@invitae.com)
# with lots of help from ECO (eric.olivares@invitae.com)

import time, os
from collections import OrderedDict
from xml.etree import ElementTree as ET

from exceptions import InteropFileNotFoundError
from utils import dmesg, select_file_from_aliases
from filemaps import XML_FILEMAP

class InteropMetadata(object):
    """Parser for sequencer's XML files describing a single run. Supply with directory to instantiate.

    CHANGES:
        
        0.2     cleaner logical process for using the various XML files. No longer throws exceptions.
        0.1     first released version.
    """
    
    __version = 0.2     # version of this parser.

    def __init__(self, xmldir):
        """Takes the absolute path of a sequencing run data directory as sole required variable.
           Attempts to parse CompletedJobInfo.xml (or viable alias). If not available, uses 
           runParameters.xml and/or runInfo.xml, which have some overlapping info (but not all).
           
           Individual parsers can be explicitly called via their respective methods.
           
           Be aware that parsing methods are DESTRUCTIVE to existing instance data."""

        self.xmldir = xmldir
        self.experiment_name = ""        # "RU1453:::/locus/data/run_data//1337/1453"
        self.investigator_name = ""      # "Locus:::Uncle_Jesse - 612 - MiSeq"
        self.runID = ""                  # cf CompletedJobInfo.xml / RTARunInfo / Run param "Id"
        self.start_datetime = None
        self.end_datetime = None
        self.rta_run_info = { }

        # read_config: a list of dictionaries, each of which describe a single read from the sequencer.
        self.read_config = []
        
        # Flow cell layout: necessary to enable parsing of different machine types' binaries.
        self.flowcell_layout = { }
                
        # Read numbers from ResequencingRunStats.xml 
        # Example: { 'clusters_raw': 19494893, 'clusters_PF': 17381252, 
        #            'unindexed': 508055, 'unindexed_PF': 16873197, 
        #            'unaligned': 18572490, 'unaligned_PF': 16973197 }   
        self.resequencing_stats = {}

        if self.get_xml_path('reseqstats') is not None:
            self.parse_ResequencingRunStats(self.get_xml_path('reseqstats'))
        
        # CompletedJobInfo.xml is the most complete XML file in the set for what we need,
        # However, only RunInfo.xml and/or RunParameters.xml will be available during an active run.
        # Getting read_config and flowcell_layout are top priority since they inform the binary parsers.
        #
        # TODO: xml_flex (proposed improvement allowing a config file to set which tokens are required / not required.)
        #       Also we might want to specify priority of provenance (e.g. get start_datetime from 'runparams' first).
        #       If you (yes YOU) have any opinions about this, please email me: naomi.most@invitae.com

        self._xml_map = OrderedDict({ 'completed': [None, self.parse_CompletedJobInfo], 
                                      'runinfo':   [None, self.parse_RunInfo],
                                      'runparams': [None, self.parse_RunParameters] })
        self._set_xml_map()
        
        # cycle through XML files, filling from what's available.
        for codename in self._xml_map:
            if self._xml_map[codename][0] is not None:
                self._xml_map[codename][1](self._xml_map[codename][0])
                if codename == 'completed':
                    break

    def _set_xml_map(self):
        "finds all available XML files and assigns them to an ordered dictionary mapping of codename:[filepath,parse_function]"
        for codename in self._xml_map:
            self._xml_map[codename][0] = self.get_xml_path(codename)
                
    def get_xml_path(self, codename):
        "returns absolute path to XML file represented by data 'codename' or None if not available."
        result = select_file_from_aliases(codename, XML_FILEMAP, self.xmldir)
        return result

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
        """Parses ResequencingRunStatistics.xml (or viable alias) to fill instance variables."""
        
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
        """parses CompletedJobInfo.xml (or viable alias) to fill instance variables."""

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
        # TODO: xml_flex
        try:
            self.investigator_name = header_ET.find("InvestigatorName").text
            self.project_name = header_ET.find("ProjectName").text
            self.experiment_name = header_ET.find("ExperimentName").text
        except AttributeError:
            pass

        # RTARunInfo / Run / *          
        self.runID = run_ET.attrib["Id"] 
        self.parse_Run_ET(run_ET)

    def parse_RunParameters(self, filepath):
        """partially implemented, not essential. Can fill read_config but not flowcell_layout."""

        tree = ET.parse(filepath)
        root = tree.getroot()

        # TODO: xml_flex - designate source priority for tokens found in multiple sources. 
        #self.runID = root.find("RunID").text
        
        # TODO: normalize this variable
        #self.start_datetime = root.find('RunStartDate').text    # format: 130208 YYMMDD

        self.experiment_name = root.find('ExperimentName').text

        self.read_config = []
        for item in root.find('Reads'):
            #Different format from that in CompletedJobInfo.xml (contains read Number)
            self.read_config.append( {'read_num': int(item.attrib['Number']),
                                      'cycles': int(item.attrib['NumCycles']), 
                                      'is_index': True if item.attrib['IsIndexedRead']=='Y' else False } )


    def parse_RunInfo(self, filepath):
        "parses Reads, Date, Flowcell, Instrument out of runInfo.xml"
        tree = ET.parse(filepath)
        run_ET = tree.getroot().find('Run')     #little of use in this file except <Run> subelement. 
        
        self.runID = run_ET.attrib['Id']
        
        #? is this useful information? if so, what for?  (It's not in CompletedJobInfo.xml)
        #self.runNumber = run_ET.attrib['Number']    
        
        self.rta_run_info = self.parse_Run_ET(run_ET)
        
    def prettyprint_read_config(self):
        out = "Read Config:"
        for read in self.read_config:
            out += "    Read %i: %i cycles %s" % (read['read_num'], read['cycles'], 
                                    "(Index)" if read['is_index'] else "")
        return out

    def prettyprint_flowcell_layout(self):
        out = """Flowcell Layout:
        Tiles: %(tilecount)i
        Lanes: %(lanecount)i
        Surfaces: %(surfacecount)i
        Swaths: %(swathcount)i""" % self.flowcell_layout
        return out

    def __str__(self):
        "Print the most important metadata (flowcell layout and read config)"
        out = self.prettyprint_read_config() + "\n"
        out += self.prettyprint_flowcell_layout() + "\n"
        return out


