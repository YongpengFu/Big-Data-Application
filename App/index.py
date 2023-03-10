# ‘dbc’ are dash boostrap components, ‘dcc’ are dash core components,  ‘html’ are dash html components and "dmc" is Dash Mantine Components
from dash import html, dcc, Input, Output, State
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from datetime import datetime
import pandas as pd
import plotly.express as px
import io
import pathlib
# Connect to main app.py file
from app import app1
from app import server

# Load the Forecast Template for downloading.
DATA_PATH = pathlib.Path(__file__).parent.joinpath("./datasets").resolve()

'''
The following template comes from https://medium.com/analytics-vidhya/python-dash-data-visualization-dashboard-template-6a5bff3c2b76
'''

'''
Some CSS styles
'''
# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'top': 0,
    'padding': '20px 10px'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9'
}

# A control panel:
controls = dbc.Card(
    [
        html.P('Dropdown', style={
            'textAlign': 'center'
        }),
        dcc.Dropdown(
            id='dropdown',
            options=[{
                'label': 'Value One',
                'value': 'value1'
            }, {
                'label': 'Value Two',
                'value': 'value2'
            },
                {
                    'label': 'Value Three',
                    'value': 'value3'
            }
            ],
            value=['value1'],  # default value
            multi=True
        ),
        html.Br(),
        html.P('Range Slider', style={
            'textAlign': 'center'
        }),
        dcc.RangeSlider(
            id='range_slider',
            min=0,
            max=10,
            step=5,
            value=[5, 10]
        ),
        html.P('Check Box', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.Checklist(
            id='check_list',
            options=[{
                'label': 'Value One',
                'value': 'value1'
            },
                {
                    'label': 'Value Two',
                    'value': 'value2'
            },
                {
                    'label': 'Value Three',
                    'value': 'value3'
            }
            ],
            value=['value1', 'value2'],
            inline=True
        )]),
        html.Br(),
        html.P('Radio Items', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.RadioItems(
            id='radio_items',
            options=[{
                'label': 'Value One',
                'value': 'value1'
            },
                {
                    'label': 'Value Two',
                    'value': 'value2'
            },
                {
                    'label': 'Value Three',
                    'value': 'value3'
            }
            ],
            value='value1',
            style={
                'margin': 'auto'
            }
        )]),
        html.Br(),
        dbc.Button(
            id='submit_button',
            n_clicks=0,
            children='Submit',
            color='primary'
        ),
    ]
)

# create a side bar
sidebar = html.Div(
    [
        html.H2('Control Panel', style=TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(
    [
        html.H2('Data 608 Amazon Headphones Analysis', style=TEXT_STYLE),
        html.Hr()
    ],
    style=CONTENT_STYLE
)


app1.layout = html.Div([sidebar, content])
# run app. debug = True allows the server to refresh every time you update you code
if __name__ == "__main__":
    app1.run(port=8051, debug=True)
