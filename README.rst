******************************************************
Illuminate: shedding light on Illumina sequencing runs
******************************************************

Python module and utilities to parse the metrics binaries output by Illumina sequencers.

Illuminate parses the metrics binaries that result from Illumina sequencer runs, and provides usable data in the form of python dictionaries and dataframes.
Intended to emulate the output of Illumina SAV, illuminate allows you to print sequencing run metrics to the command line as well as work with the data programmatically.

This package was built with versatility in mind. There is a section in this README for each of the following typical use cases::

  Running illuminate on the command line
  Using illuminate as a python module
  Parsing orphan binaries (e.g. just ErrorMetrics.bin)

Also, as of version 0.5, Illuminate supports the reading of active (in-progress) sequencing runs for Tile, Index, and Quality metrics.

But first you'll need to get set up. Jump to "Requirements" below.

Supported machines and files
----------------------------

Currently, the following Illumina machines are supported (any number of indices)::

  HiSeq
  MiSeq

As of version 0.6.0, illuminate supports all v4 binaries and all previous formats to v4.

The integrated command-line reporter currently serves the following xml files::

  RunInfo.xml
  CompletedJobInfo.xml
  ResequencingRunStatistics.xml

...and the following binary files::

  tile (InterOp/TileMetrics.bin)
  quality (InterOp/QMetrics.bin)
  index (InterOp/IndexMetrics.bin)
  control (InterOp/ControlMetrics.bin)
  corrected intensity (InterOp/CorrectedIntensityMetrics.bin)
  extraction (InterOp/ExtractionMetrics.bin)
  error (InterOp/ErrorMetrics.bin)

(Note: binaries may also be named "XxXxOut.bin"; this is an alias.)

Requirements
------------

You'll need a UNIX-like environment to use this package. Both OS X and Linux have been confirmed to work.
Illuminate relies on five open-source packages available through the Python cheeseshop::

  numpy
  pandas
  bitstring
  docopt
  xmltodict

Please let the maintainer of this package (Naomi.Most@invitae.com) know if any of these requirements make it difficult to use and integrate Illuminate in your software; this is useful feedback.

Note: if you must use a version of pandas prior to 0.14, you should pin
your version of illuminate to 0.5.7.3.

Optional but Recommended: IPython
---------------------------------

Because Illuminate is currently not geared towards interactive usage, if you want to play 
with the data, your best bet is to use iPython.  All of the parsers run from the command
line were written with loading-in to iPython.

Install ipython via pypi:

.. code-block:: bash

  $ pip install ipython
  
More installation options and instructions are available on `the iPython installation page <http://ipython.org/ipython-doc/stable/install/install.html>`_.

Once you have iPython installed, you'll be able to run illuminate or any of the
standalone parsers on your data and immediately (well, after a few seconds of parsing)
have a data dictionary and a dataframe at your disposal. See also "Parsing Orphan Binaries".

How To Install Illuminate via Pip
---------------------------------

The latest most stable version of Illuminate can be installed from the Python cheeseshop
However, some vagaries of python package management make automatic installaion of all of
the dependencies a bit problematic.

You'll need to explicitly install numpy and pandas first:

.. code-block:: bash

  $ sudo pip install numpy pandas

Once this completes, you can try:

.. code-block:: bash

  $ sudo pip install illuminate

The remaining requirements (bitstring and docopt) should come along for the ride,
and you'll be good to go.  Jump down to "Illuminate as a Command Line Tool" 
to immediately start illuminating your own data.

If you want some sample data to play with, grab Illuminate from its mercurial
repository on bitbucket.org (see next section).

How To Install Illuminate from BitBucket
----------------------------------------

The latest evelopment versions of illuminate come from its repository on bitbucket.org

Clone this repository using Mercurial (hg):

.. code-block:: bash

  $ hg clone https://hg@bitbucket.org/invitae/illuminate

For integrated use in other code as well as for running the command-line utilities, it is 
recommended (though not required) to use virtualenv to create a virtual Python environment 
in which to set up this package's dependencies.

Follow the directions on this page (https://pypi.python.org/pypi/virtualenv) for 
virtualenv, then, within your intended working directory, type:

.. code-block:: bash

  $ virtualenv ve
  $ source ve/bin/activate

Now run the following command within the same directory:

.. code-block:: bash

  (ve) $ pip install numpy pandas

The above process can take many minutes (cup of tea, perhaps?) and throw off many warnings, 
but in the end it should say this::

  Successfully installed numpy pandas python-dateutil pytz six
  Cleaning up...

If you get an error saying you are missing Python.H, you will need to install the python development
package for your system. For example, on Ubuntu or Debian, you'd do::

  $ sudo apt-get install python-dev

With numpy and pandas installed, now type:

.. code-block:: bash

  (ve) $ python setup.py build install

When these commands complete, you should be ready to roll.

You'll also have a set of sample MiSeq metrics XML and binaries you can use to test the tool.
Look in /path/to/illuminate-repo/sampledata

Illuminate as a Command Line Tool
---------------------------------

As of version 0.5.5, illuminate has been packaged for use as a command line tool. Installing system-wide via pip
(i.e. without setting up the virtualenv) will allow you to use `illuminate` anywhere. 

Important note: always check the --help option after installing a new version of Illuminate. 
Please consider the command-line tool Very Beta until version 1.0.
 
This package includes some MiSeq and HiSeq data (metrics and metadata only) from live 
sequencing runs so you can see how things work.

Activate your virtualenv (if you're going that route):

.. code-block:: bash

  $ source ve/bin/activate
  
Now enter the following to run the integrated parser against one of the test datasets:

.. code-block:: bash

  (ve) $ illuminate --tile --quality --index sampledata/MiSeq-samples/2013-04_01_high_PF/

NEW IN 0.5.6: Output raw data to CSV. You'll probably want to use `--outpath` / `-o` as well. 

The string in --outpath should be a relative or absolute directory path that already 
exists and is writeable by the illuminate user.

For example:

.. code-block:: bash

  (ve) $ illuminate --extraction --outpath /data/dump /path/to/dataset

...which produces the file: `/data/dump/runID/extraction.csv`

"runID" comes from the metadata parsing of the XML.  You can set this name yourself, instead:

.. code-block:: bash

  (ve) $ illuminate --extraction -o /data/dump --name RUN_1234 /path/to/dataset

Another option for filename output is --timestamp / -t which stamps each file with a 
datetime.now() seconds-since-Unix-epoch.  This timestamp will be the same for each
parsed file per illuminate run (in other words, you'll get matching timestamps for each
metrics file produced).

You have the ability to get higher verbosity status messages during the parsing process
by specifying `--verbose` / `-v`.  

The `--debug` / `-d` does nothing (right now) other than produce timestamps and raise the
verbosity of the output (same as -v). These messages are placed such that you can use
the timestamps to evaluate the processing time of parsing.

Finally, a fun way to explore the data is to use the `--interactive` / `-i` option to load
the dataset object directly into iPython. (This suppresses the normal printouts.)

.. code-block:: bash

  (ve) $ illuminate -i /path/to/dataset

Within iPython, you'll have the myDataset object at your disposal. This leads us naturally
to a discussion of how to use illuminate in code.

Using Illuminate as a Python Module
-----------------------------------

Illuminate was made to be integrated in code to make it easy to report on sequencing runs.

The usual way to start is to instantiate a "dataset" through the InteropDataset class,  
providing it with a valid run path, like so:

.. code-block:: python

  from illuminate import InteropDataset
  myDataset = InteropDataset('/path/to/data/')

When this class is built, the RunInfo.xml or CompletedJobInfo.xml metadata files will be
read, filling important variables like Flowcell Layout and Read Configuration.

The binary parsers are not run until they are specifically requested. Many parsing operations
can take several seconds, depending on the size of the binary file.

.. code-block:: python

  tilemetrics = myDataset.TileMetrics()
  qualitymetrics = myDataset.QualityMetrics()
  indexmetrics = myDataset.IndexMetrics()
  controlmetrics = myDataset.ControlMetrics()
  corintmetrics = myDataset.CorrectedIntensityMetrics()
  extractionmetrics = myDataset.ExtractionMetrics()
  errormetrics = myDataset.ErrorMetrics()

Note that not all run data will contain all binaries. Particularly, ErrorMetrics.bin will be 
missing if no errors were recorded / reported by the sequencer.

In the vast majority of cases, variables and data structures closely resemble the names 
and structures in the XML and BIN files that they came from.  All XML information comes 
through the InteropMetadata class, which can be accessed through the meta attribute of 
InteropDataset:

.. code-block:: python

  metadata = myDataset.meta
  
InteropDataset caches parsing data after the first run. To get a fresh re-parse of any 
file, supply "True" as the sole parameter to any parser method:

.. code-block:: python

  tm = myDataset.TileMetrics(True)

Using the Results
-----------------

The two main methods you have access to in every parser class are the data dictionary
and the DataFrame, accessed as .data and .df respectively.

Each parser produces a "data" dictionary from the raw data.  The data dict reflects
the format of the binary itself, so each parser has a slightly different set of keys.
For example::

  TileMetrics.data.keys() 

...produces::

  ['tile', 'lane', 'code', 'value']
  
This dictionary is used to set up a `pandas <http://pandas.pydata.org/>`_ DataFrame, a tutorial for which is outside the
scope of this document, but here's `an introduction to data structures in Pandas <http://pandas.pydata.org/pandas-docs/dev/dsintro.html>`_ to get you going.

Parsing Orphan Binaries
-----------------------

If you just have a single binary file, you can run the matching parser from the command line:

.. code-block:: bash

  $ ipython -i illuminate/error_metrics.py sampledata/MiSeq-samples/2013-04_10_has_errors/InterOp/TileMetricsOut.bin 

The parsers are designed to exist apart from their parent dataset, so it's possible to call 
any one of them without having the entire dataset directory at hand. However, some parsers 
(like TileMetrics and QualityMetrics) rely on information about the Read Configuration and/or 
Flowcell Layout (both pieces of data coming from the XML).

Illuminate has been seeded with some typical defaults for MiSeq, but if you are using a HiSeq,
or you know you have a different configuration, supply read_config and flowcell_layout as named 
arguments to these parsers, like so:

.. code-block:: python

  from illuminate import InteropTileMetrics  
  tilemetrics = InteropTileMetrics('/path/to/TileMetrics.bin',
                         read_config = [{'read_num': 1, 'cycles': 151, 'is_index': 0},
                                        {'read_num': 2, 'cycles': 6, 'is_index': 1},
                                        {'read_num': 3, 'cycles': 151, 'is_index':0}],
                         flowcell_layout = { 'lanecount': 1, 'surfacecount': 2,
                                             'swathcount': 1, 'tilecount': 14 } )

More Sample Data
----------------

More sample data from MiSeq and HiSeq machines will be found in the 
`Downloads <https://bitbucket.org/invitae/illuminate/downloads>`_
section of this bitbucket repository.

If you'd like to contribute sample data, contact the maintainer of 
this repository (naomi@nthmost.com) along with a brief description.

Support and Maintenance
-----------------------

This library was developed in-house at InVitae, a CLIA-certified genetic diagnostics 
company that offers customizable, clinically-relevant sequencing panels, as a response to 
the need to emulate Illumina SAV's output in a programatically accessible way.

`Invitae <https://invitae.com>`_ currently uses these parsers in conjunction with site-specific reporting scripts to 
produce automated sequencing run metrics as a check on the health of the run and the machines 
themselves.

This tool was intended from the beginning to be generalizable and open-sourced to the public.
It comes with the MIT License, meaning you are free to modify it for commercial and non-
commercial uses; just don't try to sell it as-is.

Contributions, extensions, bug reports, suggestions, and swear words all happily accepted, 
in that order.

naomi@nthmost.com
2013-present

