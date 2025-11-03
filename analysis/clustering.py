from logger import Logger
from data_cleaning import DataCleaning
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


# TODO: PCA after clustering
# TODO: scatter plot to visualize clusters


def main():
    logger = Logger()
    filepath = r'C:\Data\hltv'

    dc = DataCleaning(logger, filepath)
    df = dc.third_stage_df()

    features_x = df.select_dtypes(include=['float64', 'int64'])

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(features_x)

    # elbow plot; the results indicates that for k=5 the rate of decrease in WCSS significantly slows down
    # elbow_plot(x_scaled)

    df['cluster'] = assign_clusters(x_scaled, k=5)


def assign_clusters(x, k):
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(x)
    return labels


# helps identify the optimal k
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


if __name__ == '__main__':
    main()
