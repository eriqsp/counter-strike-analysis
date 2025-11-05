import plotly.express as px
from cleaning import DataCleaning
from clustering import final_data
from logger import Logger
import os
from dotenv import load_dotenv
load_dotenv()


# TODO: use dash + plotly for interactive plot
# TODO: try 3D plot (for 3 PCs)


# mapping the clusters to the in-game roles; the first set of keys represents the number of clusters
roles = {
    4: {
        0: "IGL\Support",
        1: "AWPer",
        2: "Entry Fragger",
        3: "Lurker"
    },

    5: {
        0: "Support",
        1: "AWPer",
        2: "Entry Fragger",
        3: "Lurker",
        4: "IGL"
    }
}


logger = Logger()
filepath = os.getenv('FILEPATH')

logger.log('Cleaning data...')
dc = DataCleaning(logger, filepath, verbose=False)
df = dc.third_stage_df()

n_clusters = 4
df_plot = final_data(df, logger, n_clusters=n_clusters, n_components=2)
df_plot['role'] = df_plot['cluster'].map(roles[n_clusters])


fig = px.scatter(
    df_plot,
    x='PC1', y='PC2',
    color='role',
    hover_name='player',
    title=f'{n_clusters} clusters (PCA Projection)',
    color_discrete_sequence=px.colors.qualitative.Set1
)

fig.update_layout(
    legend_title_text='role',
    legend=dict(
        title_font=dict(size=14),
        font=dict(size=12),
        itemsizing='trace',
        orientation='v',
        x=1.02,
        y=1
    ),
    width=900,
    height=750
)

fig.show()
