import plotly.express as px
from cleaning import DataCleaning
from clustering import final_data
from logger import Logger
import os
from dotenv import load_dotenv
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import plotly.io as pio


load_dotenv()
logger = Logger()
filepath = os.getenv('FILEPATH')

# mapping the clusters to the in-game roles; the first set of keys represents the number of clusters
roles = {
    4: {
        0: r"IGL\Support",
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


logger.log('Cleaning data...')
dc = DataCleaning(logger, filepath, verbose=False)
df = dc.third_stage_df()


def clustered_df(n_clusters=4, n_components=2):
    df_plot = final_data(df, logger, n_clusters=n_clusters, n_components=n_components)
    df_plot['role'] = df_plot['cluster'].map(roles[n_clusters])
    return df_plot


def generate_fig(dimension=2, n_clusters=4):
    if dimension == 3:
        fig = px.scatter_3d(
            clustered_df(n_clusters=n_clusters, n_components=3),
            x='PC1', y='PC2', z='PC3',
            color='role',
            hover_name='player',
            title=f'{n_clusters} clusters',
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig.update_layout(
            scene=dict(
                xaxis_title='',
                yaxis_title='',
                zaxis_title=''
            )
        )
    else:
        fig = px.scatter(
            clustered_df(n_clusters=n_clusters),
            x='PC1', y='PC2',
            color='role',
            hover_name='player',
            title=f'{n_clusters} clusters',
            color_discrete_sequence=px.colors.qualitative.Set1
        )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><extra></extra>"
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        legend_title_text='role',
        legend=dict(
            title=None,
            font=dict(size=12),
            itemsizing='trace',
            orientation='v',
            x=0.9, y=0.9
        ),
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#1e1e1e",
        margin=dict(t=50, b=50)
    )
    return fig


pio.templates.default = 'plotly_dark'
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title='Counter-Strike', assets_folder=os.path.join(os.getcwd(), "../assets"))

app.layout = dbc.Container([
    html.Div([
        html.Img(src=app.get_asset_url('cs_logo.png'), style={'width': '50px'}),
        html.H1("Professional Players - Roles", style={'display': 'inline-block', 'margin': '10px', 'vertical-align': 'left', 'color': 'white'})
    ], style={'display': 'flex', 'align-items': 'center', 'padding': '20px'}),

    html.Div(style={'height': '30px'}),

    dbc.Row([
        dbc.Row([
            dbc.Col(
                dcc.Graph(figure=generate_fig(dimension=2, n_clusters=4)),
                width=6
            ),
            dbc.Col(
                dcc.Graph(figure=generate_fig(dimension=2, n_clusters=5)),
                width=6
            ),
        ], className='mb-5'),

        dbc.Row([
            dbc.Col(
                dcc.Graph(figure=generate_fig(dimension=3, n_clusters=4)),
                width=6
            )
        ], className='mb-5')
    ])
], fluid=True, style={'backgroundColor': '#121212', 'minHeight': '100vh', 'paddingBottom': '50px'})


if __name__ == '__main__':
    app.run(debug=True)
