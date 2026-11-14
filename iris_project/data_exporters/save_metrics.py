import os
import pandas as pd

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@data_exporter
def export_data(df, *args, **kwargs):
    df.to_csv('iris_metrics.csv', index=False)
    print('Saved metrics table to iris_metrics.csv')
    return df

@test
def test_output(*args):
    assert os.path.exists('iris_metrics.csv'), 'iris_metrics.csv file was not created'
    df = pd.read_csv('iris_metrics.csv')
    assert len(df) == 4, 'Metrics CSV must have exactly 4 records'