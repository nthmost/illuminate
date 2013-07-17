ILLUMINATE
==========

Python module and utilities to parse the metrics binaries output by Illumina sequencers.

Illuminate parses the metrics binaries that result from Illumina sequencer runs, and 
provides usable data in the form of python dictionaries and dataframes.

Intended to emulate the output of Illumina SAV, illuminate allows you to print sequencing run
metrics to the command line as well as work with the data programmatically.

This package was built with versatility in mind. There is a section in this README for each
of the following typical use cases::

  Running illuminate on the command line
  Using illuminate as a python module
  Parsing orphan binaries (e.g. just ErrorMetrics.bin) 


Supported machines and files
----------------------------

Currently, only the following machines are supported (with any number of indices)::  

  HiSeq 
  MiSeq

The integrated command-line reporter currently serves the following metrics/files::

  tile (InterOp/TileMetrics.bin) 
  quality (InterOp/QMetrics.bin)
  index (InterOp/IndexMetrics.bin)
  CompletedJobInfo.xml
  ResequencingRunStatistics.xml

Unintegrated parsers for the following binaries:: 

  control (InterOp/ControlMetrics.bin)
  corrected intensity (InterOp/CorrectedIntensityMetrics.bin)
  extraction (InterOp/ExtractionMetrics.bin)
  error (InterOp/ErrorMetrics.bin)

(Note: binaries may also be named "XxXxOut.bin"; this is an alias.)


Requirements
------------

You'll need a UNIX-like environment to use this package. Both OS X and Linux have been 
confirmed to work.


How To Install
--------------

Currently this package is only available through its repository on bitbucket.org.

Clone this repository using Mercurial (hg)::

  hg clone ssh://hg@bitbucket.org/nthmost/illuminate

For integrated use in other code as well as for running the command-line utilities,
it is recommended (though not required) to use virtualenv to create a virtual Python 
environment in which to set up this package's dependencies.

Follow the directions on this page for virtualenv, then, within your intended working
directory, type::

  virtualenv ve
  source ve/bin/activate

Now run the following command in this directory::

  pip install numpy pandas

This command can take many minutes (cup of tea, perhaps?) and throw off many warnings,
but in the end it should say this::

  Successfully installed numpy pandas python-dateutil pytz six
  Cleaning up...

Next, type::

  python setup.py build
  python setup.py install

When these commands complete, you should be ready to roll.


Basic Usage From Command Line
-----------------------------

This package includes some MiSeq and HiSeq data (metrics and metadata only) from live 
sequencing runs so you can see how things work.

Within your virtualenv (see "How to Install" above), 



Basic Usage Within a Script
---------------------------

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


More Background, Support, Maintenance
-------------------------------------

Illumina's metrics data, until recently, could only be parsed and interpreted via
Illumina's proprietary "SAV" software which only runs on Windows and can't be used as
a resource in any capacity.

This library was developed in-house at InVitae, a CLIA-certified genetic diagnostics 
company that offers customizable, clinically-relevant next-generation sequencing panels, 
as a response to the need to emulate Illumina SAV's output in a program-accessible way.

InVitae currently uses these parsers in conjunction with site-specific reporting scripts
to produce automated sequencing run metrics as a check on the health of the run and the
machines themselves.

The intent from the beginning was to battle-harden this tool and then release it open-source,
given the apparent widespread need for such a thing.  Other libraries in other languages
exist, but Illuminate is currently the only one written in Python.

This package will be sporadically maintained by its main author, Naomi Most (nthmost).
Contributions, suggestions, bug reports, and swear words are welcome. More of the former
than the latter, please.

naomi.most@invitae.com
Spring 2013
