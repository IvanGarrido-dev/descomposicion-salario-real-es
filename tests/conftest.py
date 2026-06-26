import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

DATA_DIR = os.path.join(ROOT, "data")
GOLDEN = os.path.join(HERE, "golden_es.csv")


@pytest.fixture(scope="session")
def es():
    from data_loading import load_country
    return load_country("ES", DATA_DIR)


@pytest.fixture(scope="session")
def result_default(es):
    from decomposition import decompose
    return decompose(es, deflator="cne_p31", renorm=True, period=(1996, 2019))
