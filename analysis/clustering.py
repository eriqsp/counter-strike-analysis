from logger import Logger
from cleaning import DataCleaning
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np


# TODO: collect and identify in-game roles for each cluster (opener, awper, closer, etc.)


def final_data(logger: Logger, filepath: str, n_clusters: int, n_components: int, elbow=False):
    logger.log('Cleaning data...')
    dc = DataCleaning(logger, filepath, verbose=False)
    df = dc.third_stage_df()

    features_x = df.select_dtypes(include=['float64', 'int64'])

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(features_x)

    # elbow plot; the results indicates that for k=5 the rate of decrease in WCSS significantly slows down. k=4 seems good too
    if elbow:
        logger.log('Generating elbow plot...')
        elbow_plot(x_scaled)
        exit()

    logger.log('Assigning clusters (using k-means)...')
    df['cluster'] = assign_clusters(x_scaled, k=n_clusters)

    logger.log('Applying PCA...')
    return apply_pca(x_scaled, df, n_components=n_components)


# applying PCA to reduce dimension and then visualize the clusters
def apply_pca(x, df_players, n_components=2):
    pca = PCA(n_components=n_components)
    x_pca = pca.fit_transform(x)

    # compute how much the new PCA variables explain the original set of variables
    explained_variance_ratio = pca.explained_variance_ratio_
    cumulative_explained_variance = np.cumsum(explained_variance_ratio)
    print(f'Total explained variance: {cumulative_explained_variance[-1]:.2f}')

    df = pd.DataFrame(x_pca, columns=[f'PC{i}' for i in range(1, n_components + 1)])
    df['player'] = df_players['players']
    df['cluster'] = df_players['cluster']
    return df


def assign_clusters(x, k=5):
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(x)
    return labels


# helps find the optimal k (number of clusters)
def elbow_plot(x):
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=42)
        kmeans.fit(x)
        wcss.append(kmeans.inertia_)  # inertia_ is the WCSS (Within-Cluster Sum of Squares)

    plt.figure(figsize=(8, 6))
    plt.plot(range(1, 11), wcss, marker='o', linestyle='--')
    plt.title('Elbow Method for Optimal K')
    plt.xlabel('Number of Clusters (K)')
    plt.ylabel('WCSS')
    plt.grid(True)
    plt.show()
