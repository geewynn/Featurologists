import pandas as pd

from featurologists.clients.kafka import iterate_data


def test_iterate_data():
    df = pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
    assert list(iterate_data(df)) == [[1, 3], [2, 4]]
