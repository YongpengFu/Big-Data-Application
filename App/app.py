import dash
import dash_bootstrap_components as dbc


# meta_tags are required for the app layout to be mobile responsive
app1 = dash.Dash(__name__, suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'},
                            ],
                # This is important when you use container and col and row grid
                external_stylesheets=[dbc.themes.BOOTSTRAP]
                )

# Give a name of the website shown in the browser
app1.title = "Amazon Headphones Sentiment Analysis"
# This is necessary for heroku
server = app1.server