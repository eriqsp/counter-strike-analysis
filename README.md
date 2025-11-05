# Player Clustering
The idea of this project is to retrieve and analyze professional Counter Strike players' statistics.
The final goal is to use the unsupervised learning algorithm K-means to cluster the players and separate them into in-game roles.

It is an end-to-end project: web-scraping, data handling, feature engineering and modeling. The data is extracted from the website hltv.org


## About the performance check
I am checking the performance using the data available online from the players, manually checking if the players
from the same role are in the same cluster. One alternative would be to build a list with players and roles 
and then check the cluster performance based off on the list.

## Feature selection
I have tried to add another features like "traded" and "flash assists" but the clusters got worst
(players that are clearly from different roles were in the same cluster\role and vice-versa).
At the same, I think it would be great to see the clustering performance after adding more features, like
number of awp kills (I couldn't get it as easily)

## Number of clusters
The optimal number of clusters is 4 right now - for the available and chosen features.
The roles in this case are:

- Cluster 0 > IGL\Support
- Cluster 1 > AWPer
- Cluster 2 > Entry Fragger
- Cluster 3 > Lurker

## PCA
I've applied the PCA (Principal Component Analysis) framework after the clustering to visualize the clusters
in a 2D space. In this case, 2 PCs explain 64% of the total number of variables (6). 3 PCs explain 79%.
In the 2D space you can have a clear view of the clusters and its boundaries.
The next step is to make a 3D plot figure to see if the clustering can get clearer.
