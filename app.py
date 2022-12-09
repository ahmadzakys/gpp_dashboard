# 1. Import Dash
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd
from statistics import mode
import plotly.express as px

# 2. Create a Dash app instance
app = dash.Dash(
    external_stylesheets=[dbc.themes.JOURNAL],
    name = 'Global Power Plant'
    )
app.title = 'Power Plant Dashboard Analytics'

## -----Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
    ],
    brand="Global Power Plant Dashboard Analytics",
    brand_href="#",
    color="grey",
    dark=True,
)

## ----- Import Dataset GPP
gpp=pd.read_csv('power_plant.csv')


## ----- Card Content
total_country = [
    dbc.CardHeader('Number of Country'),
    dbc.CardBody([
        html.H1(gpp['country_long'].nunique())
    ]),
]
total_pp = [
    dbc.CardHeader('Number Power Plant'),
    dbc.CardBody([
        html.H1(gpp['name of powerplant'].nunique())
    ]),
]
total_fuel = [
    dbc.CardHeader('Most Used Fuel', style={"color":"black"}),
    dbc.CardBody([
        html.H1(f"{mode(gpp['primary_fuel'])} = {len(gpp[gpp['primary_fuel']==(gpp.describe(include='object')).loc['top','primary_fuel']])}")
    ])
]


## ----- Visualization
#### Choloropeth
# Data aggregation
agg1 = pd.crosstab(
    index=[gpp['country code'], gpp['start_year']],
    columns='No of Power Plant'
).reset_index()

# Visualization
plot_map = px.choropleth(agg1.sort_values(by="start_year"),
             locations='country code',
             color_continuous_scale='tealgrn',
             color='No of Power Plant',
             animation_frame='start_year',
             template='ggplot2')

#### Barplot: Ranking
# Data aggregation
gpp_indo = gpp[gpp['country_long'] == 'Indonesia']


## -----LAYOUT-----
app.layout = html.Div(children=[
    navbar,
    
    html.Br(),

    ## --Component Main Page--
    html.Div([
        ## --ROW1--
        dbc.Row([
            ### --COLUMN1--
            dbc.Col(
                [
                    dbc.Card(total_country, color='Coral'),
                    html.Br(),
                    dbc.Card(total_pp, color='Chocolate'),
                    html.Br(),
                    dbc.Card(total_fuel, color='BurlyWood'),
                ],
                width=3),

            ### --COLUMN2--
            dbc.Col([
                dcc.Graph(figure=plot_map),
            ],width=9),
        ]),

        html.Hr(),

        ## --ROW2--
        dbc.Row([
            ### --COLUMN1--
            dbc.Col([
                html.H1('Analysis by Country'),
                dbc.Tabs([
                    ## ---Tab1 : Ranking
                    dbc.Tab(
                        dcc.Graph(
                            id='plot_ranking',
                        ),
                        label='Ranking'),
                    ## ---Tab2 : Distribution
                    dbc.Tab(
                        dcc.Graph(
                            id='plot_distribution',
                        ),
                        label='Distribution'),
                ]),
            ],
            width=8),

            ### --COLUMN2--
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Select Country'),
                    dbc.CardBody(
                        dcc.Dropdown(
                            id='choose_country',
                            options=gpp['country_long'].unique(),
                            value='Indonesia',
                        ),
                    ),
                ]),
                dcc.Graph(
                    id='plot_pie',
                ),
            ],
            width=4),
        ]),
    ], style={
        'paddingLeft':'30px',
        'paddingRight':'30px',
    })

])

### Callback Plot Ranking
@app.callback(
    Output(component_id='plot_ranking', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)

def update_plot1(country_name):
    # Data aggregation
    gpp_indo = gpp[gpp['country_long'] == country_name]

    top_indo = gpp_indo.sort_values('capacity in MW').tail(10)

    # Visualize
    plot_ranking = px.bar(
                    top_indo,
                    x = 'capacity in MW',
                    y = 'name of powerplant',
                    template = 'ggplot2',
                    title = f'Rangking of Overall Power Plants in {str(country_name)}'
    )
    return plot_ranking

### Callback Box Plot
@app.callback(
    Output(component_id='plot_distribution', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)

def update_plot2(country_name):
    gpp_indo = gpp[gpp['country_long'] == country_name]
    plot_distribution = px.box(
                        gpp_indo,
                        color='primary_fuel',
                        y='capacity in MW',
                        template='ggplot2',
                        title= f'Distribution of capacity in MW in each fuel in {country_name}',
                        labels={
                            'primary_fuel': 'Type of Fuel'
                        }
                    ).update_xaxes(visible=False)
    return plot_distribution

### Callback Pie Plot
@app.callback(
    Output(component_id='plot_pie', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)

def update_plot3(country_name):
    # aggregation
    gpp_indo = gpp[gpp['country_long'] == country_name] 
    agg2=pd.crosstab(
        index=gpp_indo['primary_fuel'],
        columns='No of Power Plant'
    ).reset_index()

    # visualize
    plot_pie = px.pie(
                    agg2,
                    values='No of Power Plant',
                    names='primary_fuel',
                    color_discrete_sequence=['aquamarine', 'salmon', 'plum', 'grey', 'slateblue'],
                    template='ggplot2',
                    hole=0.4,
                    title=f'Distribution of fuel type in {country_name}',
                    labels={
                        'primary_fuel': 'Type of Fuel'
                    }
                )
    return plot_pie

# 3. Start the Dash server
if __name__ == "__main__":
    app.run_server()