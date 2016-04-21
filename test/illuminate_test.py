import datetime
import sys

import pytest

# tempraror for switching between different illumianate versions
sys.path.insert(0, "/Users/kohleman/Documents/PycharmProjects/illuminate")
import illuminate

__author__ = 'Manuel Kohler'


@pytest.fixture(scope="session")
def setup():
    print("*** Making sure which illuminate is used: {}".format(illuminate.__file__))
    return illuminate.InteropDataset("sampledata/HiSeq-samples/2014-02_13_average_run")


def test_metadata(setup):
    interop_dataset = setup
    read_metadata_dict = interop_dataset.Metadata().to_dict()

    expected_metadata_dict = {'flowcell_barcode': u'H8FW8ADXX', 'experiment_name': u'exome pool E',
                              'flowcell_position': u'B',
                              'runID': u'140213_D00251_0076_BH8FW8ADXX',
                              'flowcell_layout': {'tilecount': 16, 'lanecount': 2, 'surfacecount': 2, 'swathcount': 2},
                              'model': 'HiSeq 2500', 'start_datetime': datetime.datetime(2014, 2, 13, 0, 0),
                              'end_datetime': None}

    assert read_metadata_dict == expected_metadata_dict


def test_index_metrics(setup):
    interop_dataset = setup
    read_index_metrics_dict = interop_dataset.IndexMetrics().to_dict()

    expected_index_metrics = {'AAGAGA-': {'project': 'DefaultProject', 'clusters': 35353636,
                                          'name': 'XL2620-XE10546-LS6911-SQ2155-RE1089-na'},
                              'AACTCA-': {'project': 'DefaultProject', 'clusters': 55082601,
                                          'name': 'XL2620-XE10545-LS8191-SQ2153-RE1089-na'},
                              'TTCACG-': {'project': 'DefaultProject', 'clusters': 57719030,
                                          'name': 'XL2620-XE10544-LS6911-SQ2151-RE1089-na'},
                              'TGGTGG-': {'project': 'DefaultProject', 'clusters': 59137441,
                                          'name': 'XL2620-XE10543-LS8191-SQ2149-RE1089-na'},
                              'TGGCTT-': {'project': 'DefaultProject', 'clusters': 67702975,
                                          'name': 'XL2620-XE10542-LS6911-SQ2147-RE1089-na'},
                              'TGGAAC-': {'project': 'DefaultProject', 'clusters': 55447554,
                                          'name': 'XL2620-XE10541-LS8191-SQ2145-RE1089-na'}}

    assert read_index_metrics_dict == expected_index_metrics
