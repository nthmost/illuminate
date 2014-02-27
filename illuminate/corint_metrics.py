# -*- coding: utf-8 -*-

import pandas
from bitstring import BitString

from base_parser_class import InteropBinParser

class InteropCorrectedIntensityMetrics(InteropBinParser):

    __version = 0.1
    supported_versions = [2]
    codename = 'corint'

    def _init_variables(self):
        self.data = { 
                 'lane': [], 
                 'cycle': [], 
                 'tile': [], 
                 'avg_intensity': [], 
                 'avg_corint_A': [], 
                 'avg_corint_C': [], 
                 'avg_corint_T': [], 
                 'avg_corint_G': [],
                 'avg_corint_called_A': [], 
                 'avg_corint_called_C': [], 
                 'avg_corint_called_G': [], 
                 'avg_corint_called_T': [],
                 'num_nocalls': [], 
                 'num_calls_A': [], 
                 'num_calls_C': [], 
                 'num_calls_G': [], 
                 'num_calls_T': [],
                 'signoise_ratio': [] 
               }

    def parse_binary(self):
    
        bs = self.bs    #convenience assignment

        self.apparent_file_version = bs.read('uintle:8')
        self.check_version( self.apparent_file_version )
        
        recordlen = bs.read('uintle:8')  # length of each record

        # CorrectedIntMetrics.bin / CorrectedIntMetricsOut.bin 
        #
        # Contains base call metrics
        # Format:
        #   byte 0: file version number (2)
        #   byte 1: length of each record
        #   bytes (N * 48 + 2) to (N * 48 + 49): record:
        #       2 bytes: lane number (uint16)
        #       2 bytes: tile number (uint16)
        #       2 bytes: cycle number (uint16)
        #	2 bytes: average intensity (uint16) 
        #	2 bytes: average corrected int for channel A (uint16)
        #	2 bytes: average corrected int for channel C (uint16)
        #	2 bytes: average corrected int for channel G (uint16)
        #	2 bytes: average corrected int for channel T (uint16)
        #	2 bytes: average corrected int for called clusters for base A (uint16)
        #	2 bytes: average corrected int for called clusters for base C (uint16)
        #	2 bytes: average corrected int for called clusters for base G (uint16)
        #	2 bytes: average corrected int for called clusters for base T (uint16)
        #	20 bytes: number of base calls (float) for No Call and channel [A, C, G, T] respectively
        #	4 bytes: signal to noise ratio (float)

        for i in range(0,((bs.len) / (recordlen * 8 ))):  # record length in bits
            self.data['lane'].append(bs.read('uintle:16'))
            self.data['tile'].append(bs.read('uintle:16'))
            self.data['cycle'].append(bs.read('uintle:16'))
            self.data['avg_intensity'].append(bs.read('uintle:16'))
            self.data['avg_corint_A'].append(bs.read('uintle:16'))
            self.data['avg_corint_C'].append(bs.read('uintle:16'))
            self.data['avg_corint_G'].append(bs.read('uintle:16'))
            self.data['avg_corint_T'].append(bs.read('uintle:16'))
            self.data['avg_corint_called_A'].append(bs.read('uintle:16'))
            self.data['avg_corint_called_C'].append(bs.read('uintle:16'))
            self.data['avg_corint_called_G'].append(bs.read('uintle:16'))
            self.data['avg_corint_called_T'].append(bs.read('uintle:16'))
    
            # 20 bytes / 5 = 4 bytes each following records.
            self.data['num_nocalls'].append(bs.read('floatle:32'))
            self.data['num_calls_A'].append(bs.read('floatle:32'))
            self.data['num_calls_C'].append(bs.read('floatle:32'))
            self.data['num_calls_G'].append(bs.read('floatle:32'))
            self.data['num_calls_T'].append(bs.read('floatle:32'))
    
            # 4 bytes: sig/noise ratio (float)  
            self.data['signoise_ratio'].append(bs.read('floatle:32'))


        self.df = pandas.DataFrame(self.data)

        # place each metric into a coordinate plane so we can sort into reads.
        self.idf = self.make_coordinate_plane(self.df)

    def __str__(self):
        #TODO: to_str (improve output)
        out = "%i entries in CorrectedIntensityMetrics binary" % len(self.data['cycle'])
        out = "\nSample from lane/cycle/tile start:"
        out += "%s\n" % self.idf.head()
        return out
 


if __name__=='__main__':

    import sys
    
    try:
        filename = sys.argv[1]
    except:
        print "supply path to CorrectedIntensityMetrics.bin"
        sys.exit()

    CIM = InteropCorrectedIntensityMetrics(filename)
    print CIM
