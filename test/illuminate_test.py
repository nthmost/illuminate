import datetime

import pandas as pd
import pytest
from pandas.util.testing import assert_frame_equal

# temporary for switching between different illumianate versions
# sys.path.insert(0, "/Users/kohleman/Documents/PycharmProjects/illuminate")
import illuminate

__author__ = 'Manuel Kohler'


def format_date(s):
    # example date: '2014-02-14 13:10:03.462117'
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")


interop_datasets = {
    'H8FW8ADXX': illuminate.InteropDataset("sampledata/HiSeq-samples/2014-02_13_average_run"),
    '000000000-A7M8N': illuminate.InteropDataset("sampledata/MiSeq-samples/2014-02_11_50kit_single_read"),
    'HW37NBGXX': illuminate.InteropDataset("sampledata/NextSeq-samples/2016-04-04")
}

id_list = [id for id in interop_datasets.keys()]

expected_metadata = [({'flowcell_barcode': u'H8FW8ADXX',
                       'experiment_name': u'exome pool E',
                       'flowcell_position': u'B',
                       'runID': u'140213_D00251_0076_BH8FW8ADXX',
                       'flowcell_layout': {'tilecount': 16, 'lanecount': 2, 'surfacecount': 2, 'swathcount': 2},
                       'model': 'HiSeq 2500',
                       'start_datetime': datetime.datetime(2014, 2, 13, 0, 0),
                       'end_datetime': None},
                      interop_datasets['H8FW8ADXX']),
                     ({'flowcell_barcode': u'000000000-A7M8N',
                       'experiment_name': u'RU3284:::/locus/data/run_data//3270/3284',
                       'flowcell_position': '',
                       'runID': '140211_M00612_0148_000000000-A7M8N',
                       'flowcell_layout': {'tilecount': 14, 'lanecount': 1, 'surfacecount': 2, 'swathcount': 1},
                       'model': 'MiSeq',
                       'start_datetime': '2014-02-11T17:48:52.7792409-08:00',
                       'end_datetime': '2014-02-11T17:51:27.4294574-08:00'},
                      interop_datasets['000000000-A7M8N']),
                     ({'flowcell_barcode': u'HW37NBGXX',
                       'experiment_name': u'rajesh pool 2',
                       'flowcell_position': u'A',
                       'runID': u'160404_NS500318_0141_AHW37NBGXX',
                       'flowcell_layout': {'tilecount': 12, 'lanecount': 4, 'surfacecount': 2, 'swathcount': 3},
                       'model': 'NextSeq 500',
                       'start_datetime': datetime.datetime(2016, 4, 4, 0, 0),
                       'end_datetime': None},
                      interop_datasets['HW37NBGXX'])
                     ]

expected_index_metrics = [({'AAGAGA-': {'project': 'DefaultProject', 'clusters': 35353636,
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
                                        'name': 'XL2620-XE10541-LS8191-SQ2145-RE1089-na'}},
                           interop_datasets['H8FW8ADXX']),
                          ({'TGACCA': {'project': '', 'clusters': 3214106,
                                       'name': 'XL2606-XE10367-LS1464-SQ28-RE1051-na'},
                            'CGATGT': {'project': '', 'clusters': 3391105,
                                       'name': 'XL2606-XE10365-LS637-SQ26-RE1051-na'},
                            'TTAGGC': {'project': '', 'clusters': 3975491,
                                       'name': 'XL2606-XE10366-LS1699-SQ27-RE1051-na'},
                            'ATCACG': {'project': '', 'clusters': 5535708,
                                       'name': 'XL2606-XE10364-LS627-SQ25-RE1051-na'}},
                           interop_datasets['000000000-A7M8N']),
                          ({'AGTTCC': {'project': 'BSSE_QGF_44275_HW37NBGXX_1', 'clusters': 24099519,
                                       'name': 'BSSE_QGF_44275_HW37NBGXX_1'},
                            'GTGGCC': {'project': 'BSSE_QGF_44280_HW37NBGXX_1', 'clusters': 26717436,
                                       'name': 'BSSE_QGF_44280_HW37NBGXX_1'},
                            'GGCTAC': {'project': 'BSSE_QGF_44272_HW37NBGXX_1', 'clusters': 25383988,
                                       'name': 'BSSE_QGF_44272_HW37NBGXX_1'},
                            'CAGATC': {'project': 'BSSE_QGF_44268_HW37NBGXX_1', 'clusters': 13855820,
                                       'name': 'BSSE_QGF_44268_HW37NBGXX_1'},
                            'GTTTCG': {'project': 'BSSE_QGF_44281_HW37NBGXX_1', 'clusters': 28690696,
                                       'name': 'BSSE_QGF_44281_HW37NBGXX_1'},
                            'AGTCAA': {'project': 'BSSE_QGF_44274_HW37NBGXX_1', 'clusters': 24253009,
                                       'name': 'BSSE_QGF_44274_HW37NBGXX_1'},
                            'TGACCA': {'project': 'BSSE_QGF_44265_HW37NBGXX_1', 'clusters': 18896016,
                                       'name': 'BSSE_QGF_44265_HW37NBGXX_1'},
                            'ACAGTG': {'project': 'BSSE_QGF_44266_HW37NBGXX_1', 'clusters': 22606274,
                                       'name': 'BSSE_QGF_44266_HW37NBGXX_1'},
                            'TAGCTT': {'project': 'BSSE_QGF_44271_HW37NBGXX_1', 'clusters': 25471755,
                                       'name': 'BSSE_QGF_44271_HW37NBGXX_1'},
                            'GCCAAT': {'project': 'BSSE_QGF_44267_HW37NBGXX_1', 'clusters': 20628253,
                                       'name': 'BSSE_QGF_44267_HW37NBGXX_1'},
                            'TTAGGC': {'project': 'BSSE_QGF_44264_HW37NBGXX_1', 'clusters': 14627083,
                                       'name': 'BSSE_QGF_44264_HW37NBGXX_1'},
                            'ATCACG': {'project': 'BSSE_QGF_44262_HW37NBGXX_1', 'clusters': 13527550,
                                       'name': 'BSSE_QGF_44262_HW37NBGXX_1'},
                            'CTTGTA': {'project': 'BSSE_QGF_44273_HW37NBGXX_1', 'clusters': 11361316,
                                       'name': 'BSSE_QGF_44273_HW37NBGXX_1'},
                            'GTGAAA': {'project': 'BSSE_QGF_44279_HW37NBGXX_1', 'clusters': 27909050,
                                       'name': 'BSSE_QGF_44279_HW37NBGXX_1'},
                            'GATCAG': {'project': 'BSSE_QGF_44270_HW37NBGXX_1', 'clusters': 21167014,
                                       'name': 'BSSE_QGF_44270_HW37NBGXX_1'},
                            'CGTACG': {'project': 'BSSE_QGF_44282_HW37NBGXX_1', 'clusters': 28629740,
                                       'name': 'BSSE_QGF_44282_HW37NBGXX_1'},
                            'ATGTCA': {'project': 'BSSE_QGF_44276_HW37NBGXX_1', 'clusters': 24952176,
                                       'name': 'BSSE_QGF_44276_HW37NBGXX_1'},
                            'ACTTGA': {'project': 'BSSE_QGF_44269_HW37NBGXX_1', 'clusters': 13659353,
                                       'name': 'BSSE_QGF_44269_HW37NBGXX_1'},
                            'GTCCGC': {'project': 'BSSE_QGF_44278_HW37NBGXX_1', 'clusters': 29256212,
                                       'name': 'BSSE_QGF_44278_HW37NBGXX_1'},
                            'CGATGT': {'project': 'BSSE_QGF_44263_HW37NBGXX_1', 'clusters': 13891158,
                                       'name': 'BSSE_QGF_44263_HW37NBGXX_1'},
                            'CCGTCC': {'project': 'BSSE_QGF_44277_HW37NBGXX_1', 'clusters': 31190877,
                                       'name': 'BSSE_QGF_44277_HW37NBGXX_1'}},
                           interop_datasets['HW37NBGXX'])
                          ]

expected_tile_metrics = [({'cluster_density': 1069572.15625,
                           'mean_phasing': [0.0010174581054798182, 0.0, 0.0014177821340126684],
                           'mean_prephasing': [0.0013922555795033986, 0.0, 0.0013430441317723307],
                           'cluster_density_pf': 909664.6474609375,
                           'num_clusters': 396179671.0,
                           'aligned': 2.9306465876288712e-07,
                           'num_clusters_pf': 336948423.0},
                          interop_datasets['H8FW8ADXX']),
                         ({'cluster_density': 1251404.5848214286,
                           'mean_phasing': [0.00097659677876869118, 8.2693840210725148e-05],
                           'mean_prephasing': [0.00080601459125145564, -0.0044651559271317509],
                           'cluster_density_pf': 1086435.6004464286, 'num_clusters': 23492144.0, 'aligned': 0.0,
                           'num_clusters_pf': 20406033.0},
                          interop_datasets['000000000-A7M8N']),
                         ({'cluster_density': 195052.47520616319,
                           'mean_phasing': [0.0011471727789285069, 0],
                           'mean_prephasing': [0.0017082951494052799, 0],
                           'cluster_density_pf': 181926.53423394097,
                           'num_clusters': 508836048.0,
                           'aligned': 0.29068558873539724,
                           'num_clusters_pf': 473590791.0},
                          interop_datasets['HW37NBGXX'])
                         ]

expected_quality_metrics = [
    ({1: 94.23642906099548, 2: 88.87470808353756, 3: 85.6593561482059}, interop_datasets['H8FW8ADXX']),
    ({1: 95.98019801300919, 2: 70.747303995833}, interop_datasets['000000000-A7M8N']),
    ({1: 97.53153966532963, 2: 97.24238176124162}, interop_datasets['HW37NBGXX'])
    ]

expected_extraction_metrics = [({'cycle': [274, 274],
                                 'datetime': [format_date('2014-02-15 11:58:33.071519'),
                                              format_date('2014-02-15 11:58:38.545832')],
                                 'fwhm_A': [2.656717, 2.534114],
                                 'fwhm_C': [2.696131, 2.572728],
                                 'fwhm_G': [2.602308, 2.449553],
                                 'fwhm_T': [2.638664, 2.471945],
                                 'intensity_A': [6016, 5489],
                                 'intensity_C': [12024, 11318],
                                 'intensity_G': [2791, 2760],
                                 'intensity_T': [5882, 5586],
                                 'lane': [2, 2],
                                 'tile': [1207, 1214]},
                                [interop_datasets['H8FW8ADXX'], [35000, 35002]]),
                               ({'cycle': [1, 1],
                                 'datetime': [format_date('2014-02-11 22:07:30.850622'),
                                              format_date('2014-02-11 22:07:35.910629')],
                                 'fwhm_A': [2.281345, 2.278970],
                                 'fwhm_C': [2.308247, 2.310612],
                                 'fwhm_G': [2.347162, 2.315508],
                                 'fwhm_T': [2.247924, 2.229463],
                                 'intensity_A': [155, 155],
                                 'intensity_C': [514, 512],
                                 'intensity_G': [234, 231],
                                 'intensity_T': [312, 302],
                                 'lane': [1, 1],
                                 'tile': [1112, 1111]},
                                [interop_datasets['000000000-A7M8N'], [10, 12]]),
                               ({'cycle': [41, 41],
                                 'datetime': [format_date('2016-04-05 01:19:10.621578'),
                                              format_date('2016-04-05 01:19:10.633579')],
                                 'fwhm_A': [2.799408, 2.791119],
                                 'fwhm_C': [2.704321, 2.674301],
                                 'fwhm_G': [0.0, 0.0],
                                 'fwhm_T': [0.0, 0.0],
                                 'intensity_A': [4565, 4323],
                                 'intensity_C': [3537, 3404],
                                 'intensity_G': [0, 0],
                                 'intensity_T': [0, 0],
                                 'lane': [2, 2],
                                 'tile': [21301, 21201]},
                                [interop_datasets['HW37NBGXX'], [35000, 35002]])
                               ]


# print("***")
# d = interop_datasets['H8FW8ADXX'].ExtractionMetrics().df
# p = pd.DataFrame(d, index=[range(35000, 35002)])
# print(p)
# print("***")
# d = interop_datasets['000000000-A7M8N'].ExtractionMetrics().df
# p = pd.DataFrame(d, index=[range(START_INDEX, STOP_INDEX)])
# print(p)
# print("***")


@pytest.fixture(scope="session")
def setup():
    print("*** Which illuminate is used: {}".format(illuminate.__file__))
    miseq = illuminate.InteropDataset("sampledata/MiSeq-samples/2014-02_11_50kit_single_read")
    hiseq = illuminate.InteropDataset("sampledata/HiSeq-samples/2014-02_13_average_run")
    nextseq = illuminate.InteropDataset("sampledata/NextSeq-samples/2016-04-04")
    return miseq, hiseq


@pytest.mark.parametrize("expected, interop_dataset", expected_metadata, ids=id_list)
def test_metadata(expected, interop_dataset):
    assert expected == interop_dataset.Metadata().to_dict()


@pytest.mark.parametrize("expected, interop_dataset", expected_index_metrics, ids=id_list)
def test_index_metrics(expected, interop_dataset):
    assert expected == interop_dataset.IndexMetrics().to_dict()


@pytest.mark.parametrize("expected, interop_dataset", expected_tile_metrics, ids=id_list)
def test_tile_metrics(expected, interop_dataset):
    assert expected == interop_dataset.TileMetrics(True).to_dict()


@pytest.mark.parametrize("expected, interop_dataset", expected_quality_metrics, ids=id_list)
def test_quality_metrics(expected, interop_dataset):
    assert expected == interop_dataset.QualityMetrics().to_dict()


def test_error_metrics(setup):
    interop_dataset_miseq, interop_dataset = setup
    try:
        print("ErrorMetrics")
        print(interop_dataset.ErrorMetrics().df)
    except illuminate.InteropFileNotFoundError:
        print(test_error_metrics.__name__ + ": No ErrorMetricsOut.bin found!")


@pytest.mark.parametrize("expected, interop_dataset", expected_extraction_metrics, ids=id_list)
def test_extraction_metrics(expected, interop_dataset):
    read_extraction_metrics = interop_dataset[0].ExtractionMetrics()
    START_INDEX = interop_dataset[1][0]
    STOP_INDEX = interop_dataset[1][1]
    expected_extraction_metrics_df = pd.DataFrame(expected, index=[range(START_INDEX, STOP_INDEX)])
    assert_frame_equal(read_extraction_metrics.df[START_INDEX:STOP_INDEX], expected_extraction_metrics_df)


def test_corrcetedint_metrics(setup):
    interop_dataset_miseq, interop_dataset = setup
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
    interop_dataset_miseq, interop_dataset = setup
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


