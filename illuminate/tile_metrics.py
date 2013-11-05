# -*- coding: utf-8 -*-

import pandas

from base_parser_class import InteropBinParser

from utils import dmesg

class InteropTileMetrics(InteropBinParser):
    "ILMN Tile Metrics parser (child class of InteropBinParser)."

    __version = 0.4                 # version of this parser class.
    supported_versions = [2]        # version(s) of binary file that this parser handles

    # given by __init__ (from InteropBinParser):  read_config {}, flowcell_layout {}

    def _init_variables(self):
        # Map of binary's "code" to what it means. Filled during parsing.
        self.codemap = { }
    
        #filled during parsing. 'code' refers to the binary's arbitrary outcome codes for each record.

        self.data = {'lane' : [], 
                     'tile': [], 
                     'code': [], 
                     'value': [] }

        # per-read calculations of average phasing and prephasing across all tiles.
        # index reads (usually Read 2) almost always report 0.0 phasing and prephasing.
        
        self.mean_phasing = []
        self.mean_prephasing = []
        
    def _make_codemap(self):
        self.codemap = { 100: "cluster density (k/mm2)",
                101: "cluster density passing filters (k/mm2)",
                102: "number of clusters",
                103: "number of clusters passing filters",
                400: "control lane" }
        
        for read in self.read_config:
            self.codemap[200 + (read['read_num']-1) * 2] = "phasing for read %i" % read['read_num']
            self.codemap[201 + (read['read_num']-1) * 2] = "prephasing for read %i" % read['read_num']
            self.codemap[300 + read['read_num']-1] = "percent aligned for read %i" % read['read_num']

    def _get_mean_of_last_cycle(self, df):
        if df.empty:
            return 0
        else:
            return df[len(df)-self.num_tiles:].mean()['value']

    def parse_binary(self):
        "parses contents of TileMetrics.bin / TileMetricsOut.bin, file version 2."

        # Contains aggregate or read metrics by tile
        # Format:
        #   byte 0: file version number (2)
        #   byte 1: length of each record
        #   bytes (N * 10 + 2) - (N *10 + 11): record:      
        #       2 bytes: lane number (uint16)
        #       2 bytes: tile number (uint16)
        #       2 bytes: metric code (uint16)
        #       4 bytes: metric value (float)
        # Where N is the record index and possible metric codes are:
        #   code 100: cluster density (k/mm2)
        #   code 101: cluster density passing filters (k/mm2)
        #   code 102: number of clusters
        #   code 103: number of clusters passing filters
        #   code (200 + (N – 1) * 2): phasing for read N
        #   code (201 + (N – 1) * 2): prephasing for read N
        #   code (300 + N – 1): percent aligned for read N
        #   code 400: control lane

        bs = self.bs    #convenience assignment
    
        self.apparent_file_version = bs.read('uintle:8')
    
        self.check_version(self.apparent_file_version)

        recordlen = bs.read('uintle:8')  # length of each record == 10
        bs.pos = 16  # skip the following 16 bytes which are invariant here.

        #read records bytewise per specs in technote_rta_theory_operations.pdf from ILMN
        for i in range(0,((bs.len - 16) / (recordlen * 8))):  # 80 == record length in bits
            self.data['lane'].append(bs.read('uintle:16'))          #lane number
            self.data['tile'].append(bs.read('uintle:16'))          #tile number
            self.data['code'].append(bs.read('uintle:16'))          #metric code
            self.data['value'].append(bs.read('floatle:32'))        #metric value

        #make it fuzzy and mean.
        self.df = pandas.DataFrame(self.data)

        # INTERPRETATION: MOVE TO SEPARATE FUNCTION(S)
            
        pivot_sum = self.df.pivot_table('value', rows='code', aggfunc='sum')
        pivot_mean = self.df.pivot_table('value', rows='code', aggfunc='mean')
        
        try:
            self.total_cluster_density = pivot_sum[100]
        except:
            self.total_cluster_density = 0    
    
        try:
            self.total_cluster_density_pf = pivot_sum[101]
        except:
            self.total_cluster_density_pf = 0    

        # SAV: "Total Reads"  
        # ResequencingRunStatistics.xml: NumberOfClustersRaw
        try:
            self.num_clusters = pivot_sum[102]      
        except:
            self.num_clusters = 0

        # SAV: "PF Reads"  
        try:                                        
            self.num_clusters_pf = pivot_sum[103]
        except:
            self.num_clusters_pf = 0             
                                              
        # Illumina SAV displays metrics only based on the latest-created cluster density (100)
        # and cluster density passing filter (101) metrics output per tile. (The number of collections
        # of tile metrics per sequencing run seems to be variable.)  So we select out the highest-index
        # metrics encompassing all num_tiles tiles, and calculate our means based on that.
    
        self.mean_cluster_density = self._get_mean_of_last_cycle(self.df[self.df['code']==100])        
        self.mean_cluster_density_pf = self._get_mean_of_last_cycle(self.df[self.df['code']==101])

        if self.num_clusters and self.num_clusters_pf:
            self.percent_pf_clusters = 100 * float(self.num_clusters_pf / self.num_clusters)
        else:
            self.percent_pf_clusters = 0
    
        # Phasing and Prephasing averages per read
        for read in self.read_config:
            # There are only ever (lanes * tiles) entries per phasing and pre-phasing code, so 
            # we don't need to do the "last cycle" trick as above.
            try:    
                self.mean_phasing.append(pivot_mean[200 + (read['read_num']-1) * 2])
                self.mean_prephasing.append(pivot_mean[201 + (read['read_num']-1) * 2])
            except:
                self.mean_phasing.append(0)
                self.mean_prephasing.append(0)

    def __str__(self):
        out = '  Mean Cluster Density: %i' % self.mean_cluster_density
        out += '\n  Mean PF Clusters Density: %i' % self.mean_cluster_density_pf
        out += '\n  Total Clusters: %i' % self.num_clusters
        out += '\n  Total PF Clusters: %i' % self.num_clusters_pf 
        out += '\n  Percentage of Clusters PF: %f' % self.percent_pf_clusters
        out += '\n  Read - PHASING / PRE-PHASING:'
        for read_num in range(self.num_reads):
            out += '\n    %i - %f / %f' % (read_num+1, self.mean_phasing[read_num], self.mean_prephasing[read_num])
        out += '\n'
        return out

    def to_dict(self):
        return { 'cluster_density': self.mean_cluster_density, 
                 'cluster_density_pf': self.mean_cluster_density_pf,
                 'num_clusters_pf': self.num_clusters_pf,
                 'num_clusters': self.num_clusters,
                 'mean_phasing': self.mean_phasing,
                 'mean_prephasing': self.mean_prephasing }


if __name__=='__main__':
    
    import sys
    
    try:
        filename = sys.argv[1]
    except:
        print 'supply path to TileMetrics.bin (or TileMetricsOut.bin)'
        sys.exit()
    
    TM = InteropTileMetrics(filename)
    
    print 'Length of data: %i' % len(TM.data['code'])
    #print TM.df.head()
    
    #print TM.to_dict()
    
    print TM
    
