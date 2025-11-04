import plotly.express as px
from clustering import final_data
from logger import Logger
import os
from dotenv import load_dotenv
load_dotenv()


# TODO: use dash + plotly for interactive plot
# TODO: try 3D plot (for 3 PCs)


logger = Logger()
filepath = os.getenv('FILEPATH')
df_plot = final_data(logger, filepath, n_clusters=4, n_components=2)


fig = px.scatter(
    df_plot,
    x='PC1', y='PC2',
    color='cluster',
    hover_name='player',
    title='Player Clusters (PCA Projection)',
    width=900, height=700
)
fig.show()
