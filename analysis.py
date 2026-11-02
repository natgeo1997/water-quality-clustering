"""Reproducible companion to the recovered academic notebook; not a risk classifier."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

FEATURES = ['ph','Hardness','Solids','Chloramines','Sulfate','Conductivity','Organic_carbon','Trihalomethanes','Turbidity']


def prepare_features(frame):
    missing = set(FEATURES) - set(frame.columns)
    if missing:
        raise ValueError(f'Missing measurement columns: {sorted(missing)}')
    numeric = frame[FEATURES].apply(pd.to_numeric, errors='raise')
    if np.isinf(numeric.to_numpy()).any():
        raise ValueError('Infinite measurements are not supported')
    if numeric.isna().all().any():
        raise ValueError('Cannot calculate a median for an entirely missing feature')
    filled = numeric.fillna(numeric.median())
    return filled, StandardScaler().fit_transform(filled)


def run_analysis(csv_path, output_dir):
    csv_path, output_dir = Path(csv_path), Path(output_dir)
    frame = pd.read_csv(csv_path)
    if len(frame) < 10:
        raise ValueError('At least ten observations are required for this workflow')
    filled, scaled = prepare_features(frame)
    model = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels = model.fit_predict(scaled)
    if len(set(labels)) != 3:
        raise ValueError('Input does not support three distinct clusters')
    projection = PCA(n_components=2, svd_solver='full').fit(scaled)
    points = projection.transform(scaled)
    output_dir.mkdir(parents=True, exist_ok=True)
    assigned = frame.copy()
    assigned['Cluster'] = labels
    assigned.to_csv(output_dir/'clustered_observations.csv',index=False)
    filled.assign(Cluster=labels).groupby('Cluster').mean().to_csv(output_dir/'cluster_means.csv')
    counts = pd.Series(labels).value_counts().sort_index()
    inertia = [KMeans(n_clusters=k,random_state=42,n_init=10).fit(scaled).inertia_ for k in range(1,10)]
    pd.DataFrame({'k':range(1,10),'inertia':inertia}).to_csv(output_dir/'elbow.csv',index=False)
    metrics = {'observations':len(frame),'input_columns':len(frame.columns),'features':FEATURES,
               'missing_before_imputation':{k:int(v) for k,v in frame[FEATURES].isna().sum().items()},
               'imputation':'column median','scaling':'StandardScaler','random_state':42,'n_init':10,
               'cluster_counts':{str(k):int(v) for k,v in counts.items()},
               'silhouette_score_sample':float(silhouette_score(scaled,labels,sample_size=min(1000,len(frame)),random_state=42)),
               'silhouette_sample_size':min(1000,len(frame)),
               'pca_explained_variance_ratio':projection.explained_variance_ratio_.tolist(),
               'source_csv_sha256':hashlib.sha256(csv_path.read_bytes()).hexdigest(),
               'versions':{p:importlib.metadata.version(p) for p in ['numpy','pandas','scikit-learn','matplotlib']},
               'scope':'Companion rerun; cluster IDs are arbitrary, not water safety or geographic risk labels.'}
    (output_dir/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    fig, ax = plt.subplots(figsize=(8,6))
    for label in sorted(set(labels)):
        mask=labels==label
        ax.scatter(points[mask,0],points[mask,1],s=12,alpha=.55,label=f'Cluster {label}')
    ax.set(xlabel='Principal component 1',ylabel='Principal component 2',title='Companion rerun: PCA of standardized measurements')
    ax.legend();fig.tight_layout();fig.savefig(output_dir/'pca.png',dpi=160);plt.close(fig)
    fig, ax = plt.subplots(figsize=(7,4))
    ax.plot(range(1,10),inertia,marker='o');ax.set(xlabel='Number of clusters',ylabel='Inertia',title='Companion rerun: elbow curve');fig.tight_layout();fig.savefig(output_dir/'elbow.png',dpi=160);plt.close(fig)
    return metrics


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,default=Path('outputs/companion'))
    args=parser.parse_args()
    try:
        result=run_analysis(args.csv,args.output_dir)
    except (ValueError,FileNotFoundError) as error:
        parser.error(str(error))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
