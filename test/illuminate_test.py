import datetime

import pandas as pd
import pytest
from pandas.util.testing import assert_frame_equal

# temporary for switching between different illumianate versions
# sys.path.insert(0, "/Users/kohleman/Documents/PycharmProjects/illuminate")
import illuminate

__author__ = 'Manuel Kohler'


@pytest.fixture(scope="session")
def setup():
    print("*** Which illuminate is used: {}".format(illuminate.__file__))
    return illuminate.InteropDataset("sampledata/HiSeq-samples/2014-02_13_average_run")


@pytest.fixture(scope="session")
def setup_miseq():
    return illuminate.InteropDataset("sampledata/MiSeq-samples/2014-02_11_50kit_single_read")


def test_metadata(setup):
    interop_dataset = setup
    read_metadata_dict = interop_dataset.Metadata().to_dict()
    expected_metadata_dict = {'flowcell_barcode': u'H8FW8ADXX', 'experiment_name': u'exome pool E',
                              'flowcell_position': u'B',
                              'runID': u'140213_D00251_0076_BH8FW8ADXX',
                              'flowcell_layout': {'tilecount': 16, 'lanecount': 2, 'surfacecount': 2,
                                                  'swathcount': 2},
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


def test_tile_metrics(setup):
    interop_dataset = setup
    read_tile_metrics_dict = interop_dataset.TileMetrics(True).to_dict()

    expected_tile_metrics_dict = {'cluster_density': 1069572.15625,
                                  'mean_phasing': [0.0010174581054798182, 0.0, 0.0014177821340126684],
                                  'mean_prephasing': [0.0013922555795033986, 0.0, 0.0013430441317723307],
                                  'cluster_density_pf': 909664.6474609375,
                                  'num_clusters': 396179671.0,
                                  'aligned': 2.9306465876288712e-07,
                                  'num_clusters_pf': 336948423.0}

    assert read_tile_metrics_dict == expected_tile_metrics_dict


def test_quality_metrics(setup):
    interop_dataset = setup
    read_quality_metrics = interop_dataset.QualityMetrics().to_dict()
    expected_quality_metrics = {1: 94.23642906099548, 2: 88.87470808353756, 3: 85.6593561482059}
    assert read_quality_metrics == expected_quality_metrics


def test_error_metrics(setup):
    interop_dataset = setup
    try:
        print(interop_dataset.ErrorMetrics().df)
    except illuminate.InteropFileNotFoundError:
        print(test_error_metrics.__name__ + ": No ErrorMetricsOut.bin found!")


def test_extraction_metrics(setup):
    interop_dataset = setup

    read_extraction_metrics = interop_dataset.ExtractionMetrics()
    START_INDEX = 10000
    STOP_INDEX = 10002

    d = {'cycle': [79, 79],
         'datetime': [format_date('2014-02-14 13:10:03.462117'), format_date('2014-02-14 13:10:03.612126')],
         'fwhm_A': [2.634171, 2.588039],
         'fwhm_C': [2.670238, 2.627950],
         'fwhm_G': [2.579577, 2.557465],
         'fwhm_T': [2.619992, 2.579298],
         'intensity_A': [5646, 5514],
         'intensity_C': [11173, 11052],
         'intensity_G': [2986, 2905],
         'intensity_T': [5142, 5014],
         'lane': [1, 1],
         'tile': [1201, 1205]
         }

    expected_extraction_metrics_df = pd.DataFrame(d, index=[range(START_INDEX, STOP_INDEX)])
    assert_frame_equal(read_extraction_metrics.df[START_INDEX:STOP_INDEX], expected_extraction_metrics_df)


def test_corrcetedint_metrics(setup):
    interop_dataset = setup
    START_INDEX = 31000
    STOP_INDEX = 31002

    d = {'avg_corint_A': [1318, 1323],
         'avg_corint_C': [1269, 1231],
         'avg_corint_G': [1228, 1224],
         'avg_corint_T': [1289, 1295],
         'avg_corint_called_A': [4754, 4676],
         'avg_corint_called_C': [4822, 4708],
         'avg_corint_called_G': [4674, 4662],
         'avg_corint_called_T': [4669, 4655],
         'avg_intensity': [1290, 1282],
         'num_calls_A': [9.636842e-40, 9.755952e-40],
         'num_calls_C': [8.987718e-40, 9.077331e-40],
         'num_calls_G': [8.968618e-40, 9.059941e-40],
         'num_calls_T': [9.590122e-40, 9.727071e-40],
         'num_nocalls': [0.0, 0.0],
         'signoise_ratio': [8.260462, 8.143835],
         }
    midx = pd.MultiIndex(levels=[[243], [1], [1209, 1210]],
                         labels=[[0, 0], [0, 0], [0, 1]],
                         names=[u'cycle', u'lane', u'tile'])
    expected_correctedint_metrics_df = pd.DataFrame(d, index=midx)
    assert_frame_equal(interop_dataset.CorrectedIntensityMetrics().idf[START_INDEX:STOP_INDEX],
                       expected_correctedint_metrics_df)


def test_control_metrics(setup):
    interop_dataset = setup
    START_INDEX = 15350
    STOP_INDEX = 15360

    d = {'clusters': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         'control_str': ["CTE1_723bp", "CTE1_723bp", "CTE1_723bp", "CTE1_723bp", "CTE1_823bp", "CTE1_823bp",
                         "CTE1_823bp", "CTE1_823bp", "CTE1_823bp", "CTE1_823bp"],
         'index_str': ['TGGCTT', 'TGGAAC', 'AAGAGA', 'AACTCA', 'TGGTGG', 'TTCACG', 'TGGCTT', 'TGGAAC', 'AAGAGA',
                       'AACTCA'],
         'lane': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
         'read': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
         'tile': [2216, 2216, 2216, 2216, 2216, 2216, 2216, 2216, 2216, 2216]
         }

    expected_comtrol_metrics_df = pd.DataFrame(d, index=[range(START_INDEX, STOP_INDEX)])
    assert_frame_equal(interop_dataset.ControlMetrics().df[START_INDEX:STOP_INDEX], expected_comtrol_metrics_df)


def format_date(s):
    # example date: '2014-02-14 13:10:03.462117'
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")
