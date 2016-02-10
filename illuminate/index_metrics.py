# -*- coding: utf-8 -*-

import pandas
from bitstring import ReadError

from .base_parser_class import InteropBinParser


class InteropIndexMetrics(InteropBinParser):
    "ILMN Quality metrics parser (child class of InteropBinParser)."
    
    __version = 0.1             # version of this parser class.
    supported_versions = [1]    # version(s) of file that this parser supports
    codename = 'index'
    
    # this class doesn't require read_config and flowcell_layout, but 
    # some of the sanity checks it can run on the data do use them.

    def sanity_check(self):
        "Checks parser output against expectations from parameters of the run."
        #
        # This is the stub of an idea for pan-parser implementation later.
        
        # Does the number of individual records in IndexMetrics jibe w/ flowcell_layout?
        # 
        # Expect: num_records == surfaces * tiles * lanes * indexes  (e.g. MiSeq: 2 x 14 x 1 x 2 = 56)
        assert len(self.data['index_str']) == \
                  self.flowcell_layout['tilecount'] * self.flowcell_layout['surfacecount'] * \
                  len(self.results.keys()) * self.flowcell_layout['lanecount']
                
    def _init_variables(self):
        self.data = {
            'lane': [], 
            'tile': [], 
            'read': [], 
            'index_str': [], 
            'clusters': [], 
            'name_str': [], 
            'project_str': [] 
            }
            
        self.total_ix_reads_pf = 0  # sum of all index reads passing filter 
        self.results = {}        # after parsing, keyed by unique indexes. 
                                 # value = sum of PF clusters found per unique index.

    def parse_binary(self):
    
        bs = self.bs
    
        # Index Metrics (IndexMetrics.bin and IndexMetricOut.bin) 
        #   Reports the indexes count. Format:
        #   Byte 0: file version (1)
        #   Bytes( variable length): record:
        #   2 bytes: lane number(unint16)
        #   2 bytes: tile number(unint16)
        #   2 bytes: read number(unint16)
        #   2 bytes: number of bytes Y for index name(unint16)
        #   Y bytes: index name string (string in UTF8Encoding)
        #   4 bytes: num of clusters identified as index (uint32)
        #   2 bytes: number of bytes V for sample name(unint16)
        #   V bytes: sample name string (string in UTF8Encoding) 
        #       2 bytes: number of bytes W for sample project(unint16) 
        #   W bytes: sample project string (string in UTF8Encoding)

        self.apparent_file_version = bs.read('uintle:8')  # version number == "1"
        
        self.check_version( self.apparent_file_version )
        
        # Each record is of variable length. Fun!

        try:
            while True:
                lane, tile, read = bs.readlist('3*uintle:16')
                self.data['lane'].append(lane)  # lane number
                self.data['tile'].append(tile)  # tile number
                self.data['read'].append(read)  # read number

                # next 2 bytes: expected index name length in bytes.
                nextbytes = bs.read('uintle:16')
                self.data['index_str'].append(bs.read('bytes:%i' % nextbytes))  # index string

                # next 4 bytes: number of clusters identified as index (uint32)
                self.data['clusters'].append(bs.read('uintle:32'))

                # next 2 bytes: expected sample name length in bytes.
                nextbytes = bs.read('uintle:16')
                self.data['name_str'].append(bs.read('bytes:%i' % nextbytes))  # sample name

                # next 2 bytes: expected sample project string length in bytes.
                nextbytes = bs.read('uintle:16')
                self.data['project_str'].append(bs.read('bytes:%i' % nextbytes))

        except ReadError:
            #that's all, folks
            pass

        self.df = pandas.DataFrame(self.data)
        self.pivot = self.df.pivot_table('clusters', index=['index_str', 'project_str', 'name_str'], aggfunc='sum')

        # pivot now looks something like this, with any luck:
        """index_str  project_str       name_str                             
            AAACAT     CLIA - WF1265 #1  XL1510-XE2346-LS1430-SQ1000-RE1051-B1    8290786
            CTTGTA     CLIA - WF1265 #1  XL1510-XE2343-LS1429-SQ36-RE1051-A1      8582411
        """    

        self.total_ix_reads_pf = self.pivot.sum()

        # NEW (0.5.9): results dictionary now includes name_str and project_str 
        self.results = {}
        for ix in self.pivot.keys():
            #ix like ('index_str', 'project_str', 'name_str')
            self.results[ix[0]] = { 'project': ix[1], 'name': ix[2], 'clusters': self.pivot[ix] }

    def to_dict(self):
        return self.results

    def __str__(self):    
        out = '%s\n' % self.pivot
        return out 

if __name__=='__main__':

    import sys
    
    try:
        filename = sys.argv[1]
    except:
        print( 'supply path to IndexMetrics.bin (or IndexMetricsOut.bin)' )
        sys.exit()
    
    IM = InteropIndexMetrics(filename)

    print('Length of data: %i' % len(IM.data['clusters']))
    print(IM)

