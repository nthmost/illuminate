ILLUMINATE
==========

Libraries and utilities to parse the metrics binaries output by Illumina sequencers.

Machines supported::  

  HiSeq 
  MiSeq

Metrics supported by integrated reporter::

  tile (InterOp/TileMetrics.bin) 
  quality (InterOp/QMetrics.bin)
  index (InterOp/IndexMetrics.bin)
  CompletedJobInfo.xml
  ResequencingRunStatistics.xml

Available as standalone scripts/classes::

  control (InterOp/ControlMetrics.bin)
  corrected intensity (InterOp/CorrectedIntensityMetrics.bin)
  extraction (InterOp/ExtractionMetrics.bin)
  error (InterOp/ErrorMetrics.bin)

(Note: above binaries may also be named "XxXxOut.bin"; this is an alias.)


What For?
---------

This library was developed in-house at InVitae, a CLIA-certified genetic diagnostics 
company that offers customizable, clinically-relevant next-generation sequencing panels


Basic Usage
-----------

For wrapping an entire dataset and calling parsers as needed::

  from illuminate import IlluminaDataset
  myDataset = IlluminaDataset('/path/to/data/')

  tilemetrics = myDataset.TileMetrics()
  qualitymetrics = myDataset.QualityMetrics()

In the vast majority of cases, variables and data structures closely resemble the
names and structures in the XML and BIN files that they came from.

All XML information comes through the IlluminaMetadata class, which can be accessed
through the meta attribute of InteropDataset::

   metadata = myDataset.meta

IlluminaDataset caches parsing data after the first run. To get a fresh re-parse of
any file, supply "True" as the sole parameter to any parser method::

   tm = myDataset.TileMetrics(True)


Parse Orphan Binaries
---------------------

The parsers are designed to exist apart from their parent dataset, so it's possible to
call any one of them without having the entire dataset directory at hand.  However,
some parsers (like TileMetrics and QualityMetrics) rely on information about the Read
Configuration and/or Flowcell Layout (both pieces of data coming from the XML).

interop.py has been seeded with some typical defaults for MiSeq, but to play it safe,
supply read_config and flowcell_layout as named arguments to these parsers, like so::

   from interop import InteropTileMetrics
   tilemetrics = InteropTileMetrics('/path/to/TileMetrics.bin',
                            read_config=[{'read_num': 1, 'cycles': 151, 'is_index': 0},
                                         {'read_num': 2, 'cycles': 6, 'is_index': 1},
                                         {'read_num': 3, 'cycles': 151, 'is_index':0}],
                            flowcell_layout = { 'lanecount': 1, 'surfacecount': 2,
                                                'swathcount': 1, 'tilecount': 14 } )

Setting Up (development)
------------------------

(To Be Written?)

