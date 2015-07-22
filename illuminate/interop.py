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

import pandas

from .metadata import InteropMetadata
from .index_metrics import InteropIndexMetrics
from .tile_metrics import InteropTileMetrics
from .quality_metrics import InteropQualityMetrics
from .error_metrics import InteropErrorMetrics
from .corint_metrics import InteropCorrectedIntensityMetrics 
from .control_metrics import InteropControlMetrics
from .extraction_metrics import InteropExtractionMetrics

from .utils import select_file_from_aliases
from .exceptions import InteropFileNotFoundError
from .filemaps import BINFILE_DIR_NAME, XML_FILEMAP, BIN_FILEMAP

# python 2/3 compatibility
try:
    from functools import reduce
except ImportError:
    pass


class InteropDataset(object):
    """Encapsulates the physical files related to this sequencing run. 
       Absolves other classes of having to know about files and directories.
       Combines parser results to emulate Illumina Sequencing Analysis Viewer."""

    directory = ""  # supplied directory name to instantiate class (relative path)
    fullpath = ""   # calculated absolute filesystem path after instantiation
    xmldir = ""     # typically equivalent to fullpath
    bindir = ""     # typically = fullpath/Interop/

    meta = None

    def __init__(self, targetdir):
        "Supply a path (directory) that should contain XML files, with an InterOp directory within it."

        self.directory = targetdir

        # Without this initial check, we get a silent failure (and an empty dataset),
        # since the whole apparatus is built to be very forgiving of missing files. 
        if not os.path.isdir(targetdir):
            raise IOError('%s does not exist or is not a directory.' % targetdir)

        self.xmldir = self.directory
        self.bindir = os.path.join(self.directory, BINFILE_DIR_NAME)
        
        # aggregate results of parsing one or more XML files        
        self.meta = self.Metadata()
    
        # holders for the parser objects. Reference via *Metrics() classes.
        self._quality_metrics = None
        self._tile_metrics = None
        self._index_metrics = None
        self._error_metrics = None
        self._corint_metrics = None
        self._extraction_metrics = None
        self._control_metrics = None

    def get_binary_path(self, codename):
        "returns absolute path to binary file represented by data 'codename'"
        path = select_file_from_aliases(codename, BIN_FILEMAP, self.bindir)
        if path is None:
            raise InteropFileNotFoundError("No suitable binary found for {} in directory {}".format(codename, self.bindir))
        else:
            return path
    
    def Metadata(self, reload=False):
        "returns InteropMetadata class generated from this dataset's XML files"
        if self.meta == None or reload == True:
            self.meta = InteropMetadata(self.xmldir)
        return self.meta
    
    def QualityMetrics(self, reload=False):
        "Returns InteropQualityMetrics object from the 'quality' binary in this dataset."
        if self._quality_metrics == None or reload == True:
            self._quality_metrics = InteropQualityMetrics(self.get_binary_path('quality'), 
                                    flowcell_layout=self.meta.flowcell_layout,
                                    read_config=self.meta.read_config )
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

    def ControlMetrics(self, reload=False):
        "Returns InteropControlMetrics object from the 'control' binary in this dataset."
        if self._control_metrics == None or reload == True:
            self._control_metrics = InteropControlMetrics(self.get_binary_path('control'), 
                                    flowcell_layout=self.meta.flowcell_layout,
                                    read_config=self.meta.read_config )
        return self._control_metrics

    def ErrorMetrics(self, reload=False):
        "Returns InteropErrorMetrics object from the 'error' binary in this dataset."
        if self._error_metrics == None or reload == True:
            self._error_metrics = InteropErrorMetrics(self.get_binary_path('error'), 
                                    flowcell_layout=self.meta.flowcell_layout,
                                    read_config=self.meta.read_config )
        return self._error_metrics

    def ExtractionMetrics(self, reload=False):
        "Returns InteropExtractionMetrics object from the 'extraction' binary in this dataset."
        if self._extraction_metrics == None or reload == True:
            self._extraction_metrics = InteropExtractionMetrics(self.get_binary_path('extraction'), 
                                    flowcell_layout=self.meta.flowcell_layout,
                                    read_config=self.meta.read_config )
        return self._extraction_metrics

    def CorrectedIntensityMetrics(self, reload=False):
        "Returns InteropCorrectedIntensityMetrics object from the 'corint' binary in this dataset."
        if self._corint_metrics == None or reload == True:
            self._corint_metrics = InteropCorrectedIntensityMetrics(self.get_binary_path('corint'), 
                                    flowcell_layout=self.meta.flowcell_layout,
                                    read_config=self.meta.read_config )
        return self._corint_metrics

#TODO: ImageMetrics
#    def ImageMetrics(self, reload=False):
#        "returns InteropImageMetrics object from the 'image' binary in this dataset"
#        if self._image_metrics == None or reload == True:
#            self._image_metrics = InteropImageMetrics(self.get_binary_path('image'), 
#                                    flowcell_layout=self.meta.flowcell_layout,
#                                    read_config=self.meta.read_config )
#        return self._image_metrics
    
  
## Command Line helper functions below
def print_sample_dataset(ID):
    meta = ID.Metadata()

    print("")
    print("METADATA")
    print("--------")
    print(meta)
    print("")
    
    print("Resequencing Statistics:")
    print(meta.resequencing_stats)
    print("")
    
    tm = ID.TileMetrics()
    print("SUMMARY")
    print("-------")
    print("(tile metrics)\n")
    print(tm)
    print("")
    
    # QualityMetrics usually take a while...
    print("QUALITY")
    print("-------")
    qm = ID.QualityMetrics()
    print("(% >= Q30 per read)\n")
    print(qm)
    print("")

    im = ID.IndexMetrics()
    print("INDEXING")
    print("--------\n")
    print("Total Reads: %i" % tm.num_clusters)
    print("Reads PF: %i" % tm.num_clusters_pf)
    print("Percentage Reads Identified (PF): %f" % (float(im.total_ix_reads_pf / tm.num_clusters_pf)*100))
    print("")
    print(im)
    print("")

    print("ERRORS")
    print("------")
    try:
        em = ID.ErrorMetrics()
        print( "(sum of all types of errors across all reads)" )
        idf = em.make_coordinate_plane(em.df)
        print(idf.sum())
    except InteropFileNotFoundError:
        print("None. (no error metrics binary in this dataset.)")
    finally:
        print("")

    """
    print("INTENSITY")
    print("---------")
    try:
        cm = ID.CorrectedIntensityMetrics()
        print("(sample of raw data)")
        if cm is not None:
            print(cm.idf.head())
        else:
            print("CorrectedIntensityMetrics parsing failed.")
    except TypeError:
        print("No CorrectedIntensityMetrics binary in this dataset.")
    finally:
        print("")
    """

if __name__=='__main__':

    import sys

    try:
        dirname = sys.argv[1] 
    except IndexError:
        print("Supply the absolute or relative path to a directory of sequencing rundata.")
        print("Example:  python interop.py /home/username/seqruns/2013-02/0")
        sys.exit()
        
    myDataset = InteropDataset(dirname)

    #print(myDataset.meta.read_config)

    print_sample_dataset(myDataset)
    
