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

import os
import xml.etree.ElementTree as ET
from collections import OrderedDict
from datetime import datetime

import xmltodict

from .filemaps import XML_FILEMAP
from .utils import select_file_from_aliases


class InteropMetadata(object):
    """Parser for sequencer's XML files describing a single run. Supply with directory to instantiate.

    CHANGES:
        
        0.3 (in progress) Switching to xmltodict from ElementTree.
        0.2.2   runParameters supports both MiSeq and HiSeq formats.
        0.2.1   No longer prioritizing CompletedJobInfo.xml (not reliably present).
        0.2     Cleaner logical process for using the various XML files. No longer throws exceptions.
        0.1     First released version.
    """
    
    __version = 0.3     # version of this parser.

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
        
        # TODO: xml_datetimes
        # We can learn end_datetime this from the RTAComplete.txt file. 
        #    sample:  2/11/2014,17:25:13.217,Illumina RTA 1.18.42 
        #
        #...but it would be nicer if we didn't have to (more files to track, no fun).
        
        self.start_datetime = None        
        self.end_datetime = None
        
        self.rta_run_info = { 'flowcell': '', 'instrument': '', 'date': '' }

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
        
        # The main goal of parsing the XML is to find out read_config and flowcell_layout.
        # A lot of other data is available, but only these two basics are necessary.
        #
        # CompletedJobInfo.xml has the most complete data from MiSeq machines, but only exists
        # at the end of a run, and HiSeq machines don't even generate one.
        #
        # RunInfo.xml (containing just the basics) is always available during an active run.
        #
        # TODO: xml_flex (proposed improvement allowing a config file to set which tokens are required / not required.)
        #       Also we might want to specify priority of provenance (e.g. get start_datetime from 'runparams' first).
        #       If you (yes YOU) have any opinions about this, please email me: naomi.most@invitae.com

        self.machine_id = ""
        self.model = ""
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
        """finds all available XML files, assigns them to an ordered dictionary 
        mapping of codename:[filepath,parse_function] """
        for codename in self._xml_map:
            self._xml_map[codename][0] = self.get_xml_path(codename)
                
    def get_xml_path(self, codename):
        "returns absolute path to XML file represented by data 'codename' or None if not available."
        result = select_file_from_aliases(codename, XML_FILEMAP, self.xmldir)
        return result

    def parse_Run_ET(self, run_ET):
        "parses chunk of XML associated with the RTA Run Info blocks in (at least) 2 xml files."

        self.rta_run_info = { 'instrument': run_ET.find('Instrument').text,     # M00612
                              'flowcell': run_ET.find('Flowcell').text,         # 000000000-A316T
                              'date': run_ET.find('Date').text }                # 130208
    
        flowcell_ET = run_ET.find('FlowcellLayout')
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
                                      'is_index': True if item.attrib['IsIndexedRead']=='Y' else False } )      
    
    def parse_ResequencingRunStats(self, filepath):    
        """Parses ResequencingRunStatistics.xml (or viable alias) to fill instance variables."""
        
        # TODO: xmltodict conversion 

        tree = ET.parse(filepath)
        root = tree.getroot()   # should be "StatisticsResequencing"
        runstats_ET = root.find("RunStats")
        
        self.resequencing_stats = { 'clusters_raw': int(runstats_ET.find('NumberOfClustersRaw').text),
                                    'clusters_pf': int(runstats_ET.find('NumberOfClustersPF').text),
                                    'unindexed': int(runstats_ET.find('NumberOfUnindexedClusters').text),
                                    'unindexed_pf': int(runstats_ET.find('NumberOfUnindexedClustersPF').text),
                                    'unaligned': int(runstats_ET.find('NumberOfUnalignedClusters').text),
                                    'unaligned_pf': int(runstats_ET.find('NumberOfUnalignedClustersPF').text),
                                    'duplicate': int(runstats_ET.find('NumberOfDuplicateClusters').text) }

    def parse_RunInfo(self, filepath):
        "parses Reads, Date, Flowcell, Instrument out of runInfo.xml"
        
        #buf = open(filepath).read()
        #root = xmltodict.parse(buf)['RunInfo']
        
        tree = ET.parse(filepath)
        run_ET = tree.getroot().find('Run')     #little of use in this file except <Run> subelement. 
        
        self.runID = run_ET.attrib['Id']
        
        #? is runNumber useful information? if so, what for?
        #self.runNumber = run_ET.attrib['Number'] 
        
        self.parse_Run_ET(run_ET)

        if not self.read_config:
            buf = open(filepath).read()
            root = xmltodict.parse(buf)['RunInfo']
            try:
                Reads = root.get('Run')['Reads']['Read']
            except KeyError:
                pass

            for read in Reads:
                self.read_config.append(
                    {'read_num': int(read['@Number']),
                     'cycles': int(read['@NumCycles']),
                     'is_index': True if read['@IsIndexedRead'] == 'Y' else False
                     })


    def _parse_runparams(self, xml_dict):
        # Different format from that in CompletedJobInfo.xml (contains read Number).
        # And there are two possible keys to indicate the same datastructure. So fun.

        if not self.read_config:
            try:
                Reads = xml_dict.get('Reads')['Read']
            except KeyError:
                Reads = xml_dict.get('Reads')['RunInfoRead']

            for read in Reads:
                self.read_config.append(
                    {'read_num': int(read['@Number']),
                     'cycles': int(read['@NumCycles']),
                     'is_index': True if read['@IsIndexedRead']=='Y' else False 
                    } )

        self.rta_version = xml_dict.get('RTAVersion', '')
        
        rawdate = xml_dict.get('RunStartDate', '')    # format: 130208 YYMMDD
        if rawdate: 
            self.start_datetime = datetime.strptime(rawdate, '%y%m%d')
            
        self.runID = xml_dict.get('RunID', '')
        self.experiment_name = xml_dict.get('ExperimentName', '')
        self.flowcell_position = xml_dict.get('FCPosition', '')
        self.flowcell_barcode = xml_dict.get('Barcode', '')
        self.machine_id = xml_dict.get('ScannerID', '')

        # NextSeq
        if self.machine_id == '':
            self.machine_id = xml_dict.get('InstrumentID', '')
            # Although there is no A/B position we can still read it out from the run folder name
            self.flowcell_position = self.runID.split('_')[-1][0]
            self.flowcell_barcode = self.rta_run_info['flowcell']


    def parse_RunParameters(self, filepath):
        """parses runParameters.xml (or viable alias) to fill instance variables.

        Need to implement further since HiSeq output has no CompletedJobInfo.xml
        """
        buf = open(filepath).read()
        root = xmltodict.parse(buf)['RunParameters']

        # a dirty hack to figure out which version of this file we're reading.
        if 'Reads' in list(root['Setup'].keys()):
            self._parse_runparams(root['Setup'])        # HiSeq
        elif 'Reads' in list(root.keys()):
            self._parse_runparams(root)                 # MiSeq
        else:
            self._parse_runparams(root)                 # NextSeq

        self.model = self._get_model()


    def parse_CompletedJobInfo(self, filepath):
        """parses CompletedJobInfo.xml (or viable alias) to fill instance variables.
        
        Not all machines generate this file, so we avoid relying on it.
        """

        # TODO: xmltodict conversion 

        # comments show example data from a real MiSeq run (2013/02)
        tree = ET.parse(filepath)
        root = tree.getroot()       #should be "AnalysisJobInfo"
    
        # Something to be aware of: RTARunInfo contains a "version" attribute.
        # (This parser knows how to deal with version 2.)
        self.rta_version = root.find("RTARunInfo").attrib['Version']

        # original location of data output from the sequencer.
        self.output_folder = root.find("RTAOutputFolder").text 
        
        # TODO: xml_datetimes
        self.start_datetime = root.find("StartTime").text           # 2013-02-09T15:51:50.0811937-08:00
        self.end_datetime = root.find("CompletionTime").text        # 2013-02-09T16:06:44.0124452-08:00
        
        # dechunk all of the major sections we want to extract data from.
        sheet_ET = root.find("Sheet")
        header_ET = sheet_ET.find("Header")
        run_ET = root.find("RTARunInfo").find("Run")
        
        # Sheet / *
        # TODO: deprecate this attribute (can't get it from HiSeq XML)
        try:
            self.runtype = sheet_ET.find("Type").text       # MiSeq, HiSeq, etc.
        except AttributeError:
            #older (early 2012) XML files have no "Type" token.
            self.runtype = ""
                
        # Sheet / Header / *
        try:
            self.investigator_name = header_ET.find("InvestigatorName").text
            self.project_name = header_ET.find("ProjectName").text
            self.experiment_name = header_ET.find("ExperimentName").text
        except AttributeError:
            pass

        # RTARunInfo / Run / *          
        self.runID = run_ET.attrib["Id"] 
        self.parse_Run_ET(run_ET)

    def _get_model(self):
        """
        Guesses the sequencer model from the run folder name

        Current Naming schema for Illumina run folders, as far as I know,
        no documentation found on this, Illumina introduced a field called
        'InstrumentID' on the NextSeq runParameters.xml. That might be an
        option for the future

        MiSeq: 150130_M01761_0114_000000000-ACUR0
        NextSeq: 150202_NS500318_0047_AH3KLMBGXX
        HiSeq 2000: 130919_SN792_0281_BD2CHRACXX
        HiSeq 2500: 150203_D00535_0052_AC66RWANXX
        HiSeq 4000: 150210_K00111_0013_AH2372BBXX
        HiSeq X: 141121_ST-E00107_0356_AH00C3CCXX
        """

        # retired this line. getting self.machine_id from ScannerID field in _parse_runparams()
        # date, machine_id, run_number, fc_string = os.path.basename(self.runID).split("_")

        if self.machine_id.startswith("NS"):
            model = "NextSeq 500"
        elif self.machine_id.startswith("M"):
            model = "MiSeq"
        elif self.machine_id.startswith("D"):
            model = "HiSeq 2500"
        elif self.machine_id.startswith("SN"):
            model = "HiSeq 2000"
        elif self.machine_id.startswith("J"):
            model = "HiSeq 3000"
        elif self.machine_id.startswith("K"):
            model = "HiSeq 4000"
        elif self.machine_id.startswith("ST"):
            model = "HiSeq X"
        else:
            model = "Unidentified"
        return model

    def prettyprint_general(self):
        out = "General Config:\n" + \
              "Model: " + self.model + "\n" + \
              "Run Folder Name: " + os.path.basename(self.runID)
        return out

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
        """
        Print the most important metadata
        """
        out = self.prettyprint_general() + "\n"
        out += self.prettyprint_read_config() + "\n"
        out += self.prettyprint_flowcell_layout() + "\n"
        return out

    def to_dict(self):
        return {    'runID': self.runID,
                    'experiment_name': self.experiment_name,
                    'start_datetime': self.start_datetime,
                    'end_datetime': self.end_datetime,
                    'model': self.model,
                    'flowcell_layout': self.flowcell_layout,
                    'flowcell_barcode': self.flowcell_barcode,
                    'flowcell_position': self.flowcell_position, }
