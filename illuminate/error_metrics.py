# -*- coding: utf-8 -*-

import pandas

from .base_parser_class import InteropBinParser

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

        self.results = {}
        self.error_rate_dict = {}
            
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

        for i in range(0,int((bs.len) / (recordlen * 8))):  # record length in bits

            lane, tile, cycle, rate, perfect, one_err, two_err, three_err, four_err = \
                bs.readlist('3*uintle:16, floatle:32, 5*uintle:32')

            self.data['lane'].append(lane)
            self.data['tile'].append(tile)
            self.data['cycle'].append(cycle)
            self.data['rate'].append(rate)
            self.data['perfect'].append(perfect)
            self.data['one_err'].append(one_err)
            self.data['two_err'].append(two_err)
            self.data['three_err'].append(three_err)
            self.data['four_err'].append(four_err)

        self.df = pandas.DataFrame(self.data)

    def __str__(self):
        #TODO: to_str (improve output)
        out = "(sum of all types of errors across all reads)\n"
        idf = self.make_coordinate_plane(self.df)
        out += "%s\n" % idf.sum()
        return out

    def get_error_rate_dict(self):
        # Can be used to get a similar output as the SAV, which uses the mean and the standard deviation
        # Maybe there is a more elgant way to get this out?
        described_dict = self.df.groupby(['lane']).describe()['rate'].to_dict()
        for key, value in described_dict.iteritems():
            if key[0] in self.error_rate_dict:
                self.error_rate_dict[key[0]].update({key[1]: value})
            else:
                self.error_rate_dict[key[0]] = {key[1]: value}
        return self.error_rate_dict


if __name__=='__main__':
    
    import sys
    
    try:
        filename = sys.argv[1]
    except:
        print('supply path to ErrorMetrics.bin (or ErrorMetricsOut.bin)')
        sys.exit()
    
    EM = InteropErrorMetrics(filename)
    
    print('Length of data: %i' % len(EM.data['cycle']))
    print(EM)
