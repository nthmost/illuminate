# -*- coding: utf-8 -*-

import pandas

from base_parser_class import InteropBinParser

class InteropExtractionMetrics(InteropBinParser):

    __version = 0.1
    supported_versions = [2]

    def _init_variables(self):
        self.data = { 
                    'lane': [], 
                    'tile': [], 
                    'cycle': [], 
                    'fwhm_A': [], 
                    'fwhm_C': [], 
                    'fwhm_G': [], 
                    'fwhm_T': [], 
                    'intensity_A': [], 
                    'intensity_C': [], 
                    'intensity_G': [], 
                    'intensity_T': [],
                    'datetime': [],
                    'timestamp': []
                    }
        
    def parse_binary(self):
        bs = self.bs
        
        # Extraction Metrics (ExtractionMetricsOut.bin)
        # Contains extraction metrics such as fwhm (full width at half maximum) scores and raw intensities
        # Format:
        #   byte 0: file version number (2)
        #   byte 1: length of each record
        #   bytes (N * 38 + 2) - (N *38 + 39): record:
        #     2 bytes: lane number (uint16)
        #     2 bytes: tile number (uint16)
        #     2 bytes: cycle number (uint16)
        #     4 x 4 bytes: fwhm scores (float) for channel [A, C, G, T] respectively 
        #     2 x 4 bytes: intensities (uint16) for channel [A, C, G, T] respectively 
        #     8 bytes: date/time of CIF creation --> 2 x 4 bytes for date and timestamp 
        #   ...Where N is the record index

        self.apparent_file_version = bs.read('uintle:8')
        self.check_version(self.apparent_file_version)
        
        recordlen = bs.read('uintle:8')  # length of each record

        for i in range(0,((bs.len) / (recordlen * 8))):  # record length in bits
            self.data['lane'].append(bs.read('uintle:16'))
            self.data['tile'].append(bs.read('uintle:16'))
            self.data['cycle'].append(bs.read('uintle:16'))
    
            # 4 x 4 bytes: fwhm scores (float) for channel [A, C, G, T] respectively 
            self.data['fwhm_A'].append(bs.read('floatle:32'))    
            self.data['fwhm_C'].append(bs.read('floatle:32'))
            self.data['fwhm_G'].append(bs.read('floatle:32'))
            self.data['fwhm_T'].append(bs.read('floatle:32'))
    
            # 2 x 4 bytes: intensities (uint16) for channel [A, C, G, T] respectively 
            self.data['intensity_A'].append(bs.read('uintle:16'))
            self.data['intensity_C'].append(bs.read('uintle:16'))
            self.data['intensity_G'].append(bs.read('uintle:16'))
            self.data['intensity_T'].append(bs.read('uintle:16'))
    
            # 8 bytes: date/time of CIF creation
            self.data['datetime'].append(bs.read('uintle:32'))
            self.data['timestamp'].append(bs.read('uintle:32'))

        self.df = pandas.DataFrame(self.data)

        #self.idf = self.make_coordinate_plane(self.df)

    def __str__(self): 
        #TODO: better printout
        out = '%s' % self.df.head()
        return out

if __name__=='__main__':
    import sys
    
    try:
        filename = sys.argv[1]
    except:
        print 'supply path to ExtractionMetrics.bin'
        sys.exit()
    
    EM = InteropExtractionMetrics(filename)
    print EM
