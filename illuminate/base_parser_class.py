# -*- coding: utf-8 -*-

from bitstring import BitString

from utils import dmesg

#### SEQUENCER VAGARIES: flowcell_layout and read_config
#
# All binary parsers use these dicts, though each parser can have a different 
# flowcell layout set either by supplying these dicts as keyword arguments to class instantiation, 
# or by explicitly setting the flowcell_layout or read_config attrib after instantiation.
#
# Typical MiSeq parameters would be as follows:

FLOWCELL_LAYOUT_DEFAULTS = { 'lanecount': 1, 'surfacecount': 2, 'swathcount': 1, 'tilecount': 14 }

# Typical Read Configuration from a MiSeq:

READ_CONFIG_DEFAULTS = [{'read_num': 1, 'cycles': 151, 'is_index': 0}, 
                        {'read_num': 2, 'cycles': 6, 'is_index': 1}, 
                        {'read_num': 3, 'cycles': 151, 'is_index': 0}]

class InteropBinParser(object):
    "Generic binary parser for ILMN files typically found in InterOp directory. Subclass (do not use directly)."

    __version = 0.5      # version of this base class
    
    num_tiles = 0
    num_reads = 0

    def __init__(self, bitstring_or_filename, **kwargs):
        "Takes either a filename or a BitString object. Optional: flowcell_layout {}, read_config [{},]"

        self.flowcell_layout = kwargs.get('flowcell_layout', FLOWCELL_LAYOUT_DEFAULTS)
        self.read_config = kwargs.get('read_config', READ_CONFIG_DEFAULTS)

        # see if it's a filename or a bitstring (aka bitstream)
        try:
            bitstring_or_filename.all(1)    # attempts to perform the "are these bits all 1s" method
            self.bs = bitstring_or_filename
        except AttributeError:              # assume it's a filename, then.
            self.bs = BitString(bytes=open(bitstring_or_filename, 'rb').read())
            
        self.num_tiles = reduce(lambda x, y: x*y, self.flowcell_layout.values())
        self.num_reads = len(self.read_config)

        self._init_variables()

        if self.bs is None:
            dmesg("[%s] Fatal: BitString could not be created (file empty or not found)." % 
                    (self.__class__.__name__), 1)
        else:
            self.parse_binary() 

    def parse_binary(self):
        "Stub class for binary parsing."
        print "InteropBinParser: Generic Binary Parser class"
        print ""
        print "Override this method with your own parsing method." 
        print ""

    def _init_variables(self):
        "Place to initialize the instance variables required by specific parsers."
        pass
    
    def check_version(self, version_num):
        "Compare parsed binary's version against parser's supported_versions list."
        
        if version_num not in self.supported_versions:        
            dmesg("[%s] Warning: apparent file version (%i) may not be supported by this parser" % 
                (self.__class__.__name__, self.apparent_file_version), 2)

    def make_coordinate_plane(self, df, flatten=False):
        """Rework a dataframe containing lane / tile / cycle columns into a new dataframe using 
           lane-tile-cycle as a combined index -- sort of a coordinate plane."""
           
        if flatten:
            # recast the coordinate system as a descriptive index composed like so:
            # cycle * 1000000 + lane * 10000 + tile
            
            df.lane = df.lane.mul(10000)
            df.cycle = df.cycle.mul(1000000)

            # ...that way the index stays human-readable and still easily sorted and sliced.

        idf = df.set_index(['cycle','lane','tile'])

        if flatten:
            idf.index = idf.index.map(sum)
        
        return idf.sort()

    def to_dict(self):
        "Parser subclasses should override this, make it more specifically relevant."
        return self.data
