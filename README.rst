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

But first you'll need to get set up. Jump to "Requirements" below.


Supported machines and files
----------------------------

Currently, the following Illumina machines are supported (any number of indices)::

  HiSeq
  MiSeq

The integrated command-line reporter currently serves the following metrics/files::

  tile (InterOp/TileMetrics.bin)
  quality (InterOp/QMetrics.bin)
  index (InterOp/IndexMetrics.bin)
  CompletedJobInfo.xml
  ResequencingRunStatistics.xml

With standalone-only parsers for the following binaries::

  control (InterOp/ControlMetrics.bin)
  corrected intensity (InterOp/CorrectedIntensityMetrics.bin)
  extraction (InterOp/ExtractionMetrics.bin)
  error (InterOp/ErrorMetrics.bin)

(Note: binaries may also be named "XxXxOut.bin"; this is an alias.)


Requirements
------------

You'll need a UNIX-like environment to use this package. Both OS X and Linux have been confirmed to work.
Illuminate relies on three open-source packages available through the Python cheeseshop::

  numpy
  pandas
  bitstring
  docopt

Please let the maintainer of this package (Naomi.Most@invitae.com) know if any of these requirements make it difficult to use and integrate Illuminate in your software; this is useful feedback.

Optional but Recommended: IPython
---------------------------------

Because Illuminate is currently not geared towards interactive usage, if you want to play 
with the data, your best bet is to use iPython.  All of the parsers run from the command
line were written with loading-in to iPython.

Install ipython via pypi:

.. code-block:: bash

  $ pip install ipython
  
More installation options and instructions are available on `the iPython installation page <http://ipython.org/ipython-doc/stable/install/install.html>`_.

Once you have iPython installed, you'll be able to run illuminate.py or any of the
standalone parsers on your data and immediately (well, after a few seconds of parsing)
have a data dictionary and a dataframe at your disposal. See "Parsing Orphan Binaries".


How To Install Illuminate
-------------------------

Currently this package is only available through its repository on bitbucket.org (but will
soon be available through the Python Cheeseshop on pypi.org).

Clone this repository using Mercurial (hg):

.. code-block:: bash

  $ hg clone ssh://hg@bitbucket.org/nthmost/illuminate

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

  $ pip install numpy pandas

The above process can take many minutes (cup of tea, perhaps?) and throw off many warnings, 
but in the end it should say this::

  Successfully installed numpy pandas python-dateutil pytz six
  Cleaning up...

If you get an error saying you are missing Python.H, you will need to install the python development
package for your system. On Ubuntu or Debian, you'll probably do::

  apt-get install python-dev

With numpy and pandas installed, now type:

.. code-block:: bash

  $ python setup.py build install

When these commands complete, you should be ready to roll.


Basic Usage From Command Line
-----------------------------

While not intended for command-line usage, Illuminate contains a simple command-line utility
on the top-level of the directory called illuminate.py that will print out the most 
commonly looked-at statistics from Illumina SAV.



This package includes some MiSeq and HiSeq data (metrics and metadata only) from live 
sequencing runs so you can see how things work.

Activate your virtualenv (if you haven't already):

.. code-block:: bash

  $ source ve/bin/activate
  
Now enter the following to run the integrated parser against one of the test datasets:

.. code-block:: bash

  $ python illuminate.py data/MiSeq-samples/MiSeq-samples/2013-04_01_high_PF/

If all goes well, you should see the textual output of binary parsing represented in a 
human-readable format which is also copy-and-pasteable into the ipython interactive 
interpreter.

At the moment no work is planned to increase user friendliness at the command line level.
Please let the maintainer (Naomi.Most@Invitae.com) know how the command line interaction
could be more useful to you.


Basic Usage as a Module
-----------------------



For wrapping an entire dataset and calling parsers as needed:

.. code-block:: python

  from illuminate import IlluminaDataset
  myDataset = IlluminaDataset('/path/to/data/')
  tilemetrics = myDataset.TileMetrics()
  qualitymetrics = myDataset.QualityMetrics()

In the vast majority of cases, variables and data structures closely resemble the names 
and structures in the XML and BIN files that they came from.  All XML information comes 
through the IlluminaMetadata class, which can be accessed through the meta attribute of 
IlluminaDataset:

.. code-block:: python

  metadata = myDataset.meta
  
IlluminaDataset caches parsing data after the first run. To get a fresh re-parse of any 
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
  
This dictionary is used to set up `pandas <http://pandas.pydata.org/>`_ DataFrame, a tutorial for which is outside the
scope of this document, but here's `an introduction to data structures in Pandas <http://pandas.pydata.org/pandas-docs/dev/dsintro.html>`_ to get you going.


Parsing Orphan Binaries
-----------------------

If you just have a single binary file, you can run the matching parser from the command line:

.. code-block:: bash

  $ python illuminate/error_metrics.py data/MiSeq-samples/2013-04_10_has_errors/InterOp/TileMetricsOut.bin 

The parsers are designed to exist apart from their parent dataset, so it's possible to call 
any one of them without having the entire dataset directory at hand. However, some parsers 
(like TileMetrics and QualityMetrics) rely on information about the Read Configuration and/or 
Flowcell Layout (both pieces of data coming from the XML).

Illuminate has been seeded with some typical defaults for MiSeq, but if you are using a HiSeq,
or you know you have a different configuration, supply read_config and flowcell_layout as named 
arguments to these parsers, like so:

.. code-block:: Python

  from interop import InteropTileMetrics  
  tilemetrics = InteropTileMetrics('/path/to/TileMetrics.bin',
                         read_config=[{'read_num': 1, 'cycles': 151, 'is_index': 0},
                                      {'read_num': 2, 'cycles': 6, 'is_index': 1},
                                      {'read_num': 3, 'cycles': 151, 'is_index':0}],
                         flowcell_layout = { 'lanecount': 1, 'surfacecount': 2,
                                             'swathcount': 1, 'tilecount': 14 } )


Support and Maintenance
-----------------------

Illumina's metrics data, until recently, could only be parsed and interpreted via Illumina's 
proprietary "SAV" software which only runs on Windows and can't be sourced programmatically.

This library was developed in-house at InVitae, a CLIA-certified genetic diagnostics 
company that offers customizable, clinically-relevant sequencing panels, as a response to 
the need to emulate Illumina SAV's output in a program-accessible way.

InVitae currently uses these parsers in conjunction with site-specific reporting scripts to 
produce automated sequencing run metrics as a check on the health of the run and the machines 
themselves.

This tool was intended from the beginning to be generalizable and open-sourced to the public.
It comes with the MIT License, meaning you are free to modify it for commercial and non-
commercial uses; just don't try to sell it as-is.

Contributions, extensions, bug reports, suggestions, and swear words all happily accepted, 
in that order.

naomi.most@invitae.com 
Spring 2013
