#### CONFIGURABLE THINGS
#
# Configuration of filenames, paths, and types/amounts of output logging.
# (Most people will not need to edit this stuff.)

# Name of directory containing Interop binaries. Usually "InterOp".
BINFILE_DIR_NAME = "InterOp"

# BINARY and XML FILEMAPs
#
# "codenames" (rather than filenames) are used internally in InteropDataset to refer to files.
# (The files themselves contain no explicit indication of what's inside them.)
#
# The FILEMAP variables contain mappings of codename to filename, using aliases.
# to select file, since there are several different filenames out there.
# 
# The first filename to be retrievable will be the one that gets parsed, so view the list as
# a set of decreasing priorities.

BIN_FILEMAP = { 'extraction': ["ExtractionMetricsOut.bin", "ExtractionMetrics.bin"],
                'quality': ["QMetricsOut.bin", "QualityMetricsOut.bin", "QualityMetrics.bin"],
                'error': ["ErrorMetricsOut.bin", "ErrorMetrics.bin"],
                'tile': ["TileMetricsOut.bin", "TileMetrics.bin"],
                'corint': ["CorrectedIntMetricsOut.bin", "CorrectedIntensityMetricsOut.bin", "CorrectedIntMetrics.bin"],
                'control': ["ControlMetricsOut.bin", "ControlMetrics.bin"],
                'image': ["ImageMetricsOut.bin", "ImageMetrics.bin"], 
                'index': ["IndexMetricsOut.bin", "IndexMetrics.bin"] }

XML_FILEMAP = { 'runinfo': ["RunInfo.xml"],
               'runparams': ["runParameters.xml"],
               'reseqstats': ["ResequencingRunStatistics.xml"],
               'completed': ["CompletedJobInfo.xml"] }

