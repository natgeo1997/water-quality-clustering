import numpy as np
import pandas as pd
import pytest
from analysis import FEATURES, prepare_features, run_analysis


def sample():
    rng=np.random.default_rng(42)
    data=pd.DataFrame(rng.normal(size=(60,9)),columns=FEATURES)
    data.loc[0,'ph']=np.nan
    data['Potability']=rng.integers(0,2,len(data))
    return data


def test_median_imputation_excludes_target_and_scales_features():
    data=sample()
    filled,scaled=prepare_features(data)
    assert filled.loc[0,'ph']==data['ph'].median()
    assert list(filled.columns)==FEATURES and 'Potability' not in filled
    np.testing.assert_allclose(scaled.mean(axis=0),0,atol=1e-12)
    data['Potability']=1-data['Potability']
    np.testing.assert_allclose(prepare_features(data)[1],scaled)


@pytest.mark.parametrize('problem',['missing_column','all_null','infinite'])
def test_unusable_inputs_are_rejected(problem):
    data=sample()
    if problem=='missing_column': data=data.drop(columns='ph')
    elif problem=='all_null': data['ph']=np.nan
    else: data.loc[1,'ph']=np.inf
    with pytest.raises(ValueError): prepare_features(data)


def test_pipeline_outputs_retain_row_count_and_are_repeatable(tmp_path):
    data=sample();source=tmp_path/'sample.csv';data.to_csv(source,index=False)
    first=run_analysis(source,tmp_path/'one');second=run_analysis(source,tmp_path/'two')
    assert sum(first['cluster_counts'].values())==60
    assert first==second
    rows=pd.read_csv(tmp_path/'one/clustered_observations.csv')
    assert len(rows)==60 and set(rows.Cluster)=={0,1,2}
    assert len(pd.read_csv(tmp_path/'one/elbow.csv'))==9
    assert (tmp_path/'one/pca.png').is_file()
