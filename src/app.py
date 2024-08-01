import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import geopandas as gpd

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "2022 Kenya VoterData Dashboard"
# Data importing
#voters data
df=pd.read_csv("https://raw.githubusercontent.com/YonQwon/kenya_2022_voters_dashboard_app/data/voters.csv")
#geojson of subcounties
subgeo=gpd.read_file("https://raw.githubusercontent.com/YonQwon/kenya_2022_voters_dashboard_app/data/map.geojson")
#geojson of subcounties
#data wrangling
df.drop(columns="Unnamed: 0", inplace=True)

#  functions to calc topten
def top_ten(name):
    fig = px.bar(
        data_frame=df.groupby(name)["Registered Voters"].sum().sort_values(ascending=False).head(10),
        y="Registered Voters",
        color="Registered Voters",
        height=600,
        width=800,
        title=f"Top 10 {name} with most number of registered voters in Kenya",
        text="Registered Voters"
    )
    fig.update_layout(xaxis_title=name, paper_bgcolor='#111111', plot_bgcolor='#111111', font=dict(color='#7FDBFF'))
    fig.update_traces(textangle=-45)
    return fig
#calclurating bottomten
def bottom_ten(name):
    fig = px.bar(
        data_frame=df.groupby(name)["Registered Voters"].sum().sort_values(ascending=False).tail(10),
        y="Registered Voters",
        color="Registered Voters",
        height=600,
        width=800,
        title=f"Bottom 10 {name} with least number of registered voters in Kenya",
        text="Registered Voters"
    )
    fig.update_layout(xaxis_title=name, paper_bgcolor='#111111', plot_bgcolor='#111111', font=dict(color='#7FDBFF'))
    fig.update_traces(textangle=-45)
    return fig

# Layout
app.layout = dbc.Container(
    fluid=True,
    style={'backgroundColor': '#111111', 'color': '#7FDBFF', 'padding': '20px'},
    children=[
        dbc.Row(
            dbc.Col(html.H1("Kenya 2022 Voter Data Dashboard", style={'textAlign': 'center', 'color': '#7FDBFF'}))
        ),
        dbc.Row([
            dbc.Col([
                html.Label('Name of the County:', style={'color': '#7FDBFF'}),
                dcc.Dropdown(
                    id='county-dropdown',
                    options=[{'label': county, 'value': county} for county in df["County Name"].unique()],
                    value=df["County Name"].unique()[0],
                    style={'color': 'black'}
                ),
            ], width=6),
            dbc.Col([
                html.Label('Select map type:', style={'color': '#7FDBFF'}),
                dcc.Dropdown(
                    id='map-dropdown',
                    options=[
                        {'label': 'Open Street Map', 'value': 'open-street-map'},
                        {'label': 'White BG', 'value': 'white-bg'},
                        {'label': 'Carto Positron', 'value': 'carto-positron'},
                        {'label': 'Carto Darkmatter', 'value': 'carto-darkmatter'},
                        {'label': 'Stamen Terrain', 'value': 'stamen-terrain'},
                        {'label': 'Stamen Toner', 'value': 'stamen-toner'},
                        {'label': 'Stamen Watercolor', 'value': 'stamen-watercolor'}
                    ],
                    value='open-street-map',
                    style={'color': 'black'}
                ),
            ], width=6)
        ]),
        html.Div(id='county-info', style={'textAlign': 'center', 'padding': '20px 0'}),
        dbc.Tabs([
            dbc.Tab(label='Charts', children=[
                dbc.Row([
                    dbc.Col(dcc.Graph(id='bar-chart'), width=6),
                    dbc.Col(dcc.Graph(id='sunburst-chart'), width=6)
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='top-ten-counties-bar'), width=6),
                    dbc.Col(dcc.Graph(id='bottom-ten-counties-bar'), width=6)
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='top-ten-constituencies-bar'), width=6),
                    dbc.Col(dcc.Graph(id='bottom-ten-constituencies-bar'), width=6)
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='top-ten-caw-names-bar'), width=6),
                    dbc.Col(dcc.Graph(id='bottom-ten-caw-names-bar'), width=6)
                ])
            ])
        ]),
        dbc.Row(
            dbc.Col(dcc.Graph(id='map-chart'), width=12)
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    "Am Samy Migwi, an entry-level data scientist. I started this project with a PDF file from the IEBC website https://www.iebc.or.ke. I converted it to a .csv file using a Python script, cleaned the data with pandas, and combined it with a geojson file for visualization with Plotly.express. Initially, I used Dash but later switched to Streamlit. This project utilizes geopandas, pandas, numpy, json, geojson, re, plotly.express, and Dash.",
                    style={'padding': '20px', 'textAlign': 'center', 'color': '#7FDBFF'}
                )
            )
        )
    ]
)

# Callbacks
@app.callback(
    [Output('county-info', 'children'),
     Output('bar-chart', 'figure'),
     Output('sunburst-chart', 'figure'),
     Output('top-ten-counties-bar', 'figure'),
     Output('bottom-ten-counties-bar', 'figure'),
     Output('top-ten-constituencies-bar', 'figure'),
     Output('bottom-ten-constituencies-bar', 'figure'),
     Output('top-ten-caw-names-bar', 'figure'),
     Output('bottom-ten-caw-names-bar', 'figure'),
     Output('map-chart', 'figure')],
    [Input('county-dropdown', 'value'),
     Input('map-dropdown', 'value')]
)

#sd['Text'] = 'Constituency: ' + sd['Constituency'] + '<br>Registered Voters: ' + sd['Registered Voters'].astype(str)
def update_charts(selected_county, selected_map):
    mask = df[df["County Name"] == selected_county]
    dtx = mask.groupby("Constituency")["Registered Voters"].sum().sort_values(ascending=False)
    numvoters = mask["Registered Voters"].sum()
    
    fig_bar = px.bar(data_frame=dtx, color=dtx, color_continuous_scale="thermal", height=600, width=800)
    fig_bar.update_layout(paper_bgcolor='#111111', plot_bgcolor='#111111', font=dict(color='#7FDBFF'))
    
    fig_sunburst = px.sunburst(mask, path=["Constituency", "CAW Name"], values="Registered Voters", color="Registered Voters", color_continuous_scale='RdBu', width=800, height=700, title="A sunburst of voters in constituency and locations")
    fig_sunburst.update_layout(paper_bgcolor='#111111', plot_bgcolor='#111111', font=dict(color='#7FDBFF'))
    fig_sunburst.update_traces(textinfo="label+value+percent entry")
    
    top_counties_bar = top_ten("County Name")
    bottom_counties_bar = bottom_ten("County Name")
    
    top_constituencies_bar = top_ten("Constituency")
    bottom_constituencies_bar = bottom_ten("Constituency")
    
    top_caw_names_bar = top_ten("CAW Name")
    bottom_caw_names_bar = bottom_ten("CAW Name")
    
    subdf = df.groupby("Constituency")["Registered Voters"].sum()
    sd = pd.DataFrame().from_dict(subdf).reset_index()
    subgeo.rename(columns={"shapeName": "Constituency"}, inplace=True)
    subgeo["Constituency"] = subgeo["Constituency"].str.upper()
    
    fig_map = px.choropleth_mapbox(sd, geojson=subgeo, locations="Constituency", featureidkey="properties.Constituency",color="Registered Voters", hover_data=["Registered Voters"], mapbox_style=selected_map, opacity=.6, center={"lat": 0.10, "lon": 36.54}, zoom=6, height=800, width=1200,color_continuous_scale="rainbow")
    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, paper_bgcolor='#111111', font=dict(color='#7FDBFF'))
    
    return f"{selected_county} County has {numvoters} registered voters", fig_bar, fig_sunburst, top_counties_bar, bottom_counties_bar, top_constituencies_bar, bottom_constituencies_bar, top_caw_names_bar, bottom_caw_names_bar, fig_map

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=8050)
