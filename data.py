# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 09:27:15 2020
@author: Usuario
"""

import pandas as pd
import nltk
from nltk.cluster.kmeans import KMeansClusterer
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import cluster
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler, PowerTransformer, FunctionTransformer
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
import random
from sklearn.cluster import KMeans
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
import time
from sklearn.manifold import TSNE
import requests
import pandas as pd
from bs4 import BeautifulSoup


def clean_dataset(df):
    assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
    df.dropna(inplace=True)
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    return df[indices_to_keep].astype(np.float64)


def find_max_cluster(cl, dflabel, category='phising'):
    # assign cluster number with the most exchanges
    type_cluster = 0
    num_of_type = 0
    lbl_density = 0
    lbl_clus = 0
    label_den_max = 0
    label_clus_max = 0
    # print(category)
    num_cases = np.sum(dflabel['label_I'] == category)
    for clust in np.unique(cl.labels_):
        size_of_cluster = np.sum(cl.labels_ == clust)

        mask = dflabel['cluster'] == clust
        d = dflabel[mask]
        num = np.sum(d['label_I'] == category)
        density = num / num_cases
        cluster_y = num / size_of_cluster
        if num > num_of_type:
            lbl_density = density
            lbl_clus = cluster_y
            num_of_type = num
            type_cluster = clust
            if label_den_max < lbl_density:
                label_den_max = lbl_density
            if label_clus_max < lbl_clus:
                label_clus_max = lbl_clus
                # print('cluster number   {}   number of type found: {}    cluster size: {}   label density: {}'.format(clust,num,size_of_cluster,density))

    return label_den_max, label_clus_max


def cluster_fit(results, df, i):
    cl = cluster2(results, n_clusters=i)
    df['cluster'] = cl.labels_
    d, e = find_max_cluster(cl, df)
    return d, e


def data_pipeline(df):
    # strip address column
    data = df  # df.iloc[:,1:]
    log = FunctionTransformer(func=np.log1p, inverse_func=np.expm1, validate=True)
    scale = StandardScaler()
    pca = PCA(n_components=data.shape[1])

    # build pipeline
    pipe = Pipeline([('log', log),
                     ('scale', scale),
                     ('PCA', pca)])

    results = pipe.fit_transform(data)
    return pipe, results


def cluster2(results, n_clusters):
    cl2 = KMeans(n_clusters, n_init=10, max_iter=500, n_jobs=-1, verbose=0)
    return cl2.fit(results)


def clusterice(df, num):
    df.fillna(0, inplace=True)
    df['value_IN'] = df['value_IN'] / 100000000000000000
    df['week_op_mean_IN'] = df['week_op_mean_IN'] / 100000000000000000
    df['week_opp_adrrs_mean_IN'] = df['week_opp_adrrs_mean_IN'] / 100000000000000000
    df['month_mean_IN'] = df['month_mean_IN'] / 100000000000000000
    df['month_op_adress_mean_IN'] = df['month_op_adress_mean_IN'] / 100000000000000000
    df['month_opp_adrrs_max_IN'] = df['month_opp_adrrs_max_IN'] / 100000000000000000
    df['average_wk_lftm_in'] = df['average_wk_lftm_in'] / 100000000000000000
    df['value_OUT'] = df['value_OUT'] / 100000000000000000
    df['week_op_mean_OUT'] = df['week_op_mean_OUT'] / 100000000000000000
    df['week_opp_adrrs_mean_OUT'] = df['week_opp_adrrs_mean_OUT'] / 100000000000000000
    df['month_mean_OUT'] = df['month_mean_OUT'] / 100000000000000000
    df['month_op_adress_mean_OUT'] = df['month_op_adress_mean_OUT'] / 100000000000000000
    df['month_opp_adrrs_max_OUT'] = df['month_opp_adrrs_max_OUT'] / 100000000000000000
    df['average_wk_lftm_out'] = df['average_wk_lftm_out'] / 100000000000000000
    df['balance_mean'] = df['balance_mean'] / 100000000000000000

    df_2 = df.drop(['type_send', 'type_1', 'Unnamed: 0', 'Unnamed: 0.1', 'adrrs_rec_IN', 'average_wk_lftm_out',
                    'average_wk_lftm_in', 'adrrs_rec_OUT', 'star_t_IN', 'end_t_IN', 'end_t_OUT', 'star_t_OUT', 'from',
                    'to', 'main_adress', 'label_I', 'label_II', 'index', 'balance_median', 'balance_max',
                    'month_opp_adrrs_mean_IN', 'month_opp_adrrs_mean_OUT'], axis=1)
    pipe_2, results_2 = data_pipeline(df_2)
    cl_2 = cluster2(results_2, n_clusters=10)
    # original cluster
    pca = pipe_2.named_steps['PCA']
    scale = pipe_2.named_steps['scale']
    log = pipe_2.named_steps['log']
    c_2 = cl_2.cluster_centers_
    # transform back to real numbers
    centroids = log.inverse_transform(scale.inverse_transform(pca.inverse_transform(c_2)))
    maindf_summary = pd.DataFrame(centroids, columns=df_2.columns, index=np.unique(cl_2.labels_))
    # maindf_summary
    maindf_summary['label'] = maindf_summary.index
    # a = maindf_summary.columns
    # df_feats = df[df['label_I']=='phising']
    # df_feats= df[a]
    feat = {}
    for fea in df_2.columns:
        feat[fea] = 'mean'

    df_feats = df.groupby(['label_I'], as_index=False).agg(feat)
    df_feats['label'] = df_feats['label_I']
    # df_feats =df_feats[a]
    df_cos = pd.concat([maindf_summary, df_feats]).round(1)

    return df_cos