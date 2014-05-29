# -*- coding: utf-8 -*-

import pandas

from base_parser_class import InteropBinParser

class InteropErrorMetrics(InteropBinParser):

    __version = 0.1
    supported_versions = [3]
    codename = 'error'

    def _init_variables(self):
        self.data = { 'lane': [], 
                      'tile': [], 
                      'cycle': [], 
                      'perfect': [], 
                      'rate': [],
                      'one_err': [], 
                      'two_err': [], 
                      'three_err': [], 
                      'four_err': [] }
            
    def parse_binary(self):
    
        bs = self.bs
    
        # Contains cycle error rate as well as counts for perfect reads and read with 1-4 errors
        # Format:
        #   byte 0: file version number (3)
        #   byte 1: length of each record
        #   bytes (N * 30 + 2) to (N * 30 + 11): record:
        #       2 bytes: lane number (uint16)
        #       2 bytes: tile number (uint16)
        #       2 bytes: cycle number (uint16)
        #	4 bytes: error rate (float)
        #	4 bytes: number of perfect reads (uint32)
        #	4 bytes: number of reads with 1 error (uint32)
        #	4 bytes: number of reads with 2 errors (uint32)
        # 	4 bytes: number of reads with 3 errors (uint32)
        #	4 bytes: number of reads with 4 errors (uint32)
        #   ...where N is the record index.

        self.apparent_file_version = bs.read('uintle:8')
        
        self.check_version(self.apparent_file_version)
        
        recordlen = bs.read('uintle:8')  # length of each record

        for i in range(0,((bs.len) / (recordlen * 8))):  # record length in bits
            self.data['lane'].append(bs.read('uintle:16'))
            self.data['tile'].append(bs.read('uintle:16'))
            self.data['cycle'].append(bs.read('uintle:16'))
            self.data['rate'].append(bs.read('floatle:32'))
            self.data['perfect'].append(bs.read('uintle:32'))
            self.data['one_err'].append(bs.read('uintle:32'))
            self.data['two_err'].append(bs.read('uintle:32'))
            self.data['three_err'].append(bs.read('uintle:32'))
            self.data['four_err'].append(bs.read('uintle:32'))

        self.df = pandas.DataFrame(self.data)
    
    def __str__(self):
        #TODO: to_str (improve output)
        out = "(sum of all types of errors across all reads)\n"
        idf = self.make_coordinate_plane(self.df)
        out += "%s\n" % idf.sum()
        return out

    
if __name__=='__main__':
    
    import sys
    
    try:
        filename = sys.argv[1]
    except:
        print 'supply path to ErrorMetrics.bin (or ErrorMetricsOut.bin)'
        sys.exit()
    
    EM = InteropErrorMetrics(filename)
    
    print 'Length of data: %i' % len(EM.data['cycle'])
    print EM
    
