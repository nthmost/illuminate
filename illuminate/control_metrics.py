#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 3/28/2013
# by nthmost (naomi.most@invitae.com)

import pandas
from bitstring import ReadError

from .base_parser_class import InteropBinParser


class InteropControlMetrics(InteropBinParser):

    __version = 0.1
    supported_versions = [1]
    codename = 'control'

    def _init_variables(self):
        self.data = { 'lane': [], 
                      'tile': [], 
                      'read': [], 
                      'control_str': [], 
                      'index_str': [], 
                      'clusters': [] 
                    }

    def parse_binary(self):
    
        bs = self.bs

        # Control Metrics (ControlMetricsOut.bin)
        # Contains pull out information for Illumina in-line sample controls
        # Format:
        #   byte 0: file version number (1) bytes (variable length): record:
        #   2 bytes: lane number (uint16)
        #   2 bytes: tile number (uint16)
        #   2 bytes: read number (uint16)
        #   2 bytes: number bytes X for control name(uint16)
        #   X bytes: control name string (string in UTF8Encoding) 
        #   2 bytes: number bytes Y for index name(uint16)
        #   Y bytes: index name string (string in UTF8Encoding) 
        #   4 bytes: num of clusters identified as control (uint32)

        self.apparent_file_version = bs.read('uintle:8')  # version number of binary 
        self.check_version(self.apparent_file_version)

        try:
            while True:
                lane, tile, read = bs.readlist('3*uintle:16')
                self.data['lane'].append(lane)
                self.data['tile'].append(tile)
                self.data['read'].append(read)

                # next 2 bytes: expected control name length in bytes.
                nextbytes = bs.read('uintle:16')
                self.data['control_str'].append(bs.read('bytes:%i' % (nextbytes)))

                # next 2 bytes: expected index name length in bytes.
                nextbytes = bs.read('uintle:16')
                self.data['index_str'].append(bs.read('bytes:%i' % (nextbytes)))

                self.data['clusters'].append(bs.read('uintle:32'))
        except ReadError:
            pass
    
        self.df = pandas.DataFrame(self.data)

    def __str__(self):
        #TODO: to_str (improve output)
        out = "%s\n" % self.df.head()
        return out


if __name__=='__main__':

    import sys
    
    try:
        filename = sys.argv[1]
    except:
        print( "supply path to ExtractionMetrics.bin" )
        sys.exit()
    
    CM = InteropControlMetrics(filename)
    print(CM)
