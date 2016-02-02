# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import pandas

from .base_parser_class import InteropBinParser

anno_domini = datetime(1, 1, 1)

class InteropExtractionMetrics(InteropBinParser):

    __version = 0.2
    supported_versions = [2]
    codename = 'extraction'

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
        #     8 bytes: date/time of CIF creation --> serialized C# datetime object 
        #   ...Where N is the record index

        self.apparent_file_version = bs.read('uintle:8')
        self.check_version(self.apparent_file_version)
        
        recordlen = bs.read('uintle:8')  # length of each record

        for i in range(0,int((bs.len) / (recordlen * 8))):  # record length in bits

            lane, tile, cycle, fwhm_A, fwhm_C, fwhm_G, fwhm_T, intensity_A, intensity_C, intensity_G, intensity_T = \
                bs.readlist('3*uintle:16, 4*floatle:32, 4*uintle:16')

            self.data['lane'].append(lane)
            self.data['tile'].append(tile)
            self.data['cycle'].append(cycle)

            # 4 x 4 bytes: fwhm scores (float) for channel [A, C, G, T] respectively
            self.data['fwhm_A'].append(fwhm_A)
            self.data['fwhm_C'].append(fwhm_C)
            self.data['fwhm_G'].append(fwhm_G)
            self.data['fwhm_T'].append(fwhm_T)

            # 2 x 4 bytes: intensities (uint16) for channel [A, C, G, T] respectively
            self.data['intensity_A'].append(intensity_A)
            self.data['intensity_C'].append(intensity_C)
            self.data['intensity_G'].append(intensity_G)
            self.data['intensity_T'].append(intensity_T)
    
            # 8 bytes: date/time of CIF creation
            datetime_bits = bs.read(64)
            # first 2 bits of last byte represent "kind" of date
            # we don't care about "kind", so let's zero those bits
            datetime_bits.set(0, (56, 57))
            # the rest is a 62bit integer giving 100ns since midnight Jan 1, 0001
            microseconds = timedelta(microseconds=datetime_bits.uintle / 10)
            self.data['datetime'].append(anno_domini + microseconds)

        self.df = pandas.DataFrame(self.data)
        #self.idf = self.make_coordinate_plane(self.df)

    def __str__(self): 
        #TODO: to_str (improve output)
        out = "%s\n" % self.df.head()
        return out

if __name__=='__main__':

    import sys
    
    try:
        filename = sys.argv[1]
    except:
        print('supply path to ExtractionMetrics.bin')
        sys.exit()
    
    EM = InteropExtractionMetrics(filename)
    print(EM)
