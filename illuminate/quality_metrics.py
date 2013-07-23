# -*- coding: utf-8 -*-

import pandas
from utils import dmesg

from base_parser_class import InteropBinParser

class InteropQualityMetrics(InteropBinParser):
    "ILMN Quality metrics parser (child class of InteropBinParser)."

    __version = 0.2     # version of this parser class.
    supported_versions = [4]        # version(s) of file that this parser supports

    # a scalar representing the number of quality scores per record in QualityMetrics*.bin
    num_quality_scores = 50

    def _init_variables(self):
        dmesg("QM Read Config:", 2)
        dmesg(self.read_config, 2)
        self._setup_read_tiers()
        self._setup_data()

        # filled at the end of parsing.
        self.read_qscore_results = {'readnum': [], 'q30': [], 'q20': [] }

    def _setup_data(self):
        self.data = { 'lane': [], 'cycle': [], 'tile': [] }
        for qual in range(1,self.num_quality_scores+1):
            self.data['q'+str(qual)] = []

    def _setup_read_tiers(self):    
        """concocts a 'read tier' array describing the start-number of cycles per individual Read.
        (Example: read_config of 151/6/151 becomes read_tiers=[151,157,308]""" 

        self.read_tiers = []     # list of tuples

        last_tier = 0
        num_reads = len(self.read_config)
    
        for x in range(0,num_reads):
            new_tier = last_tier + self.read_config[x]['cycles'] 
            self.read_tiers.append(new_tier)
            last_tier = new_tier

        dmesg(self.read_tiers, 3)

    def index_quality(self, target_qscore=30):
        "Convenience method to return index read's % quality for target_qscore (default 30)"
    
        # Assumes only one Index read, which is true for MiSeqs but not true for HiSeqs. 
        # WillNotFix
        for read in self.read_config:
            if read['is_index']:
                return self.get_qscore_percentage(target_qscore, read['read_num']-1)

    def get_qscore_percentage(self, target_qscore=30, read_num=-1):
        "Returns % of quality scores at or above target_qscore (default 30). 2nd argument specifies read number."
    
        q_upper_cols = [x for x in self.data.keys() if x[0]=='q' and int(x[1:]) > target_qscore-1 ]
        q_upper_df = self.idf[q_upper_cols] 

        if read_num==-1:
            # return %>=qn for entire data set.
            q_upper_sum = q_upper_df.values.sum()
            q_total_sum = self.idf.values.sum()

        else:
            # segment Qscores by read_num. Let IndexError be raised in case of too-high read_num.
            # read_tiers example: [151,157,308] 
        
            cycle_start = 0 if read_num==0 else self.read_tiers[read_num-1] + 1 
            cycle_end = self.read_tiers[read_num]
        
            tiles = self.flowcell_layout['tilecount']
            lanes = self.flowcell_layout['lanecount']
            surfaces = self.flowcell_layout['surfacecount']

            i_start = 0 if read_num==0 else cycle_start * tiles * lanes * surfaces
            i_end = cycle_end * tiles * lanes * surfaces
        
            q_upper_sum = q_upper_df[i_start:i_end].values.sum()
            q_total_sum = self.idf[i_start:i_end].values.sum()  
        
        # Return a percentage (like in Illumina SAV)
        return 100 * float(q_upper_sum) / float(q_total_sum)

    def parse_binary(self):
        "Important: set read_config appropriately -- needed to construct read_tiers to separate Q scores by Read."

        bs = self.bs   
    
        # QualityMetrics format according to ILMN specs:
        #
        #   byte 0: file version number (4)
        #   byte 1: length of each record
        #   bytes (N * 206 + 2) - (N * 206 + 207): record:
        #       2 bytes: lane number (uint16)
        #       2 bytes: tile number (uint16)
        #       2 bytes: cycle number (uint16)
        #       4 x 50 bytes: number of clusters assigned score (uint32) Q1 through Q50

        self.apparent_file_version = bs.read('uintle:8')
        self.check_version(self.apparent_file_version)

        recordlen = bs.read('uintle:8')  # length of each record

        #read records bytewise per specs in technote_rta_theory_operations.pdf from ILMN
        for i in range(0,((bs.len) / (recordlen * 8))):  # 206 * 8 = 1648 record length in bits
            lane = bs.read('uintle:16')
            tile = bs.read('uintle:16')
            cycle = bs.read('uintle:16')
        
            self.data['lane'].append(lane)
            self.data['tile'].append(tile)
            self.data['cycle'].append(cycle)

            for qual in range(1, self.num_quality_scores + 1):  #(50 entries of 4 bytes each)
                self.data['q'+str(qual)].append(bs.read('uintle:32'))

        self.df = pandas.DataFrame(self.data)
    
        self.idf = self.make_coordinate_plane(self.df, flatten=True)
        
        for read_num in range(self.num_reads):
            q30 = self.get_qscore_percentage(30, read_num)
            q20 = self.get_qscore_percentage(20, read_num)
            self.read_qscore_results['readnum'].append(read_num+1)
            self.read_qscore_results['q30'].append(q30)
            self.read_qscore_results['q20'].append(q20)

    def __str__(self):
        out = ""
        for read in self.read_config:
            out += "Read %i: %f %s\n" % (read['read_num'], self.get_qscore_percentage(30, read['read_num']-1),
                                    "(Index)" if read['is_index'] else "")
        return out

    #def to_dict(self):
    #TODO: Make a dict that reports on Q30 and Q20 scores of each read.
    #    return self.read_qscore_results


if __name__=='__main__':
    
    import sys
    
    try:
        filename = sys.argv[1]
    except:
        print 'supply path to QualityMetrics.bin (or QMetricsOut.bin)'
        sys.exit()
    
    QM = InteropQualityMetrics(filename)
    
    print 'Length of data: %i' % len(QM.data['cycle'])

    qscore_df = pandas.DataFrame(QM.to_dict())
    print qscore_df
    
