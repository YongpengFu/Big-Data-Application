# ‘dbc’ are dash boostrap components, ‘dcc’ are dash core components,  ‘html’ are dash html components and "dmc" is Dash Mantine Components
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_components import Row as Row, Col as Col
from dash import callback_context
import pandas as pd
import plotly.express as px
import pathlib
import plotly.express as px
import TrainedModelLoading
# Connect to main app.py file
from app import app1
from DBConnection import Database

# Load the Forecast Template for downloading.
DATA_PATH = pathlib.Path(__file__).parent.joinpath("./datasets").resolve()

# Global variables
productList = []

# Get product details list from DB


def GetProductList():
    with Database() as db:
        return db.query("SELECT ASIN, Name, Summary, Url, Price, NumOfRating FROM Product")


def CheckForColorIndex(price, df):
    colorIndex = -1

    for i in range(len(df['range'])):
        priceRangeStr = df['range'][i]
        rangeArray = priceRangeStr.split(", ")

        if float(price) >= float(rangeArray[0]) and float(price) < float(rangeArray[1]):
            colorIndex = i
            break

    return colorIndex


def ConvertToDataFrame():
    bins = [0.0, 25.0, 50.0, 75.0, 100.0, 125.0, 150.0,
            175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0]

    df = pd.DataFrame(productList, columns=[
                      'asin', 'name', 'summary', 'rating', 'price', 'NumOfRating'])
    df = df[['price']].astype(float)
    df['range'] = pd.cut(x=df['price'], bins=bins)
    df['count'] = df.groupby('range')['range'].transform('count')
    df = df.drop(columns=['price']).drop_duplicates()
    df['range'] = df['range'].astype(str).str.replace('(', '', regex=True)
    df['range'] = df['range'].astype(str).str.replace(']', '', regex=True)
    df['sorter'] = df['range'].astype(str).str.split(", ").str[0].astype(float)
    df = df.sort_values(by=['sorter']).reset_index().dropna()
    df['category'] = [str(i) for i in df.index]

    return df


def CreateProductNameGroupItemList():
    global productList
    if not productList:
        productList = GetProductList()

    productNameList = [
        dbc.ListGroupItem(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(src=app1.get_asset_url(
                                'productImg.png'), className="product-image", width=80),
                            style={'textAlign': 'right',
                                   'padding-top': '3%', 'padding-right': '0'},
                            width=4,
                        ),
                        dbc.Col(
                            html.H4("Headphone", className="sub-header",),
                            style={'textAlign': 'left', 'padding': '0'},
                            width=8,
                        )
                    ],
                ),
            ],
            style={'background-color': '#a8c6d1', },
        )]

    for index, product in enumerate(productList):
        productNameList.append(dbc.ListGroupItem(
            product[1],
            id=str(index),
            action=True,
            className="productItem",
        ))

    return productNameList


# This component contains product name list, and product details, and our analysis.
list_group = html.Div(
    [
        dbc.Row
        ([
            dbc.Col
            (
                dbc.ListGroup(CreateProductNameGroupItemList(),
                              flush=True, className="sidebar_style"),
                width=3
            ),
            dbc.Col
            (html.Div([
                dbc.Card(id='productPriceCard',
                         className="product_analysis_card_style"),
                dbc.Card(
                    [
                        dbc.CardHeader(
                            "Trained models for sentiment analysis: ", className="CardHeaderStyle",),
                        dbc.CardBody([
                            dbc.InputGroup(
                                [dbc.Input(id="input-group-button-input",
                                           placeholder="Type your review here...",
                                           className="CardBodyStyle",),
                                 dbc.Button("Submit", id="input-group-button", n_clicks=0),],
                                className="mb-3",
                            ),
                            html.Hr(),
                            html.Div(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div("VADER: "), style={'background-color': '#dfe4e6', "padding": "10px"}, width="auto", ),
                                            dbc.Col(
                                                html.Div("Sentiment analysis...", id="VADER_Result", style={"padding": "10px"}))
                                        ], className="row_style"
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div("NLTK Naive bayes: "), style={'background-color': '#dfe4e6', "padding": "10px"}, width="auto", ),
                                            dbc.Col(
                                                html.Div("Sentiment analysis...", id="NNB_Result", style={"padding": "10px"}))
                                        ], className="row_style"
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div("SVC with TF-IDF: "), style={'background-color': '#dfe4e6', "padding": "10px"}, width="auto", ),
                                            dbc.Col(
                                                html.Div("Sentiment analysis...", id="SVCTI_Result", style={"padding": "10px"}))
                                        ], className="row_style"
                                    ),

                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div("Multinomial naive bayes with TF-IDF: "), style={'background-color': '#dfe4e6', "padding": "10px"}, width="auto", ),
                                            dbc.Col(
                                                html.Div("Sentiment analysis...", id="MABTF_Result", style={"padding": "10px"}))
                                        ], className="row_style"
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div("Multinomial naive bayes with countVectorizer: "), style={'background-color': '#dfe4e6', "padding": "10px"}, width="auto", ),
                                            dbc.Col(
                                                html.Div("Sentiment analysis...", id="MNBC_Result", style={"padding": "10px"}))
                                        ],  className="row_style"
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div("Multi-layer Perceptron classifier with countVectorizer: "), style={'background-color': '#dfe4e6', "padding": "10px"}, width="auto", ),
                                            dbc.Col(
                                                html.Div("Sentiment analysis...", id="MPCC_Result", style={"padding": "10px"}))
                                        ],  className="row_style"
                                    ),
                                ]
                            ),
                        ]),
                    ],
                    className="product_analysis_card_style"),
                dbc.Card(id='modelAccuracyGraphcard',
                         class_name="product_analysis_card_style"
                         ),
            ]),
                width=6
            ),
            dbc.Col
            (
                dbc.Card(id='productDetailCard',
                         className="product_detail_card_style"),
                width=3
            ),
        ]),
    ],
)

# This callback function will fetch the product details based on the product index


@app1.callback([
    Output("productDetailCard", "children"),
    Output("productPriceCard", "children"),
    Output("modelAccuracyGraphcard", "children")
], [Input(str(i), "n_clicks") for i in range(len(productList))])
def getProductDetails(*args):

    trigger = callback_context.triggered[0]
    indexStr = trigger["prop_id"].split(".")[0]
    index = -1
    productDetails = []
    asin = ''
    name = ''
    summary = ''
    price = ''
    NumOfRating = ''

    if indexStr:
        index = int(indexStr)

    if index != -1:
        productDetails = productList[index]

    if productDetails:
        asin = productDetails[0]
        name = productDetails[1]
        summary = productDetails[2]
        price = productDetails[4]
        NumOfRating = productDetails[5]

    productDf = ConvertToDataFrame()
    color_discrete_sequence = ['#e47911']*len(productDf)
    colorIndex = CheckForColorIndex(price, productDf)

    if colorIndex != -1:
        color_discrete_sequence[colorIndex] = '#007eb9'

    productPriceFig = px.bar(productDf, x='range', y='count',
                             color='category',
                             color_discrete_sequence=color_discrete_sequence,
                             )

    productPriceFig.update_layout(
        height=500,
        xaxis=dict(
            title='Price Range'
        ),
        yaxis=dict(
            title='Count'
        ),
        showlegend=False,
    )

    productDetailsChildren = [
        dbc.CardHeader("Name: " + str(name), className="CardHeaderStyle",),
        dbc.CardBody([
            html.H5("Review summary", className="card-title"),
            html.P(summary, className="card-text"),
            html.H5("Price", className="card-title"),
            html.P("$" + str(price), className="card-text"),
        ], className='CardBodyStyle'),
        dbc.CardFooter("Number of Rating: " + str(NumOfRating),
                       className='CardBodyStyle'),
    ]

    productPriceChildren = [
        dbc.CardHeader("Price Frequency Histogram",
                       className="CardHeaderStyle",),
        dbc.CardBody([
            dcc.Graph(figure=productPriceFig),
        ]),
    ]

    df = pd.DataFrame({
        "Models": ["MLP", "MultinomialNB-CV", "NLTK NaiveBayes", "VADER", "SVC_TF-IDF", "MultinomialNB_TF-IDF", "SVC_word2vec", "MultinomialNB_word2vec"],
        "Accuracy": [86, 83, 78.67, 78, 89, 75.14, 58.7, 58.7],
        "Labels": ["86%", "83%", "78.6%", "78%", "89%", "75.1%", "58.7%", "58.7%"]
    })
    fig_accuracy = px.bar(df, x="Models", y="Accuracy",
                          text="Labels", color_discrete_sequence=['#48a3c6'])

    modelAccuracyGraphChildren = [
        dbc.CardHeader("Model Accuracy", className="CardHeaderStyle",),
        dbc.CardBody([
            dcc.Graph(figure=fig_accuracy),
        ])
    ]

    return productDetailsChildren, productPriceChildren, modelAccuracyGraphChildren


@app1.callback(Output("VADER_Result", "children"),
               Output("NNB_Result", "children"),
               Output("MNBC_Result", "children"),
               Output("MPCC_Result", "children"),
               Output("SVCTI_Result", "children"),
               Output("MABTF_Result", "children"),
               [Input("input-group-button", "n_clicks"),
                State("input-group-button-input", "value"),],)
def sia_result(n_clicks, review):
    if n_clicks:
        if str(review).strip():
            VADER_Result = TrainedModelLoading.sia_result(str(review).strip())
            NNB_Result = TrainedModelLoading.NaiveBayesClassifier_result(
                str(review).strip())
            MNBC_Result = TrainedModelLoading.MultinomialNBCountVector_result(
                str(review).strip())
            MPCC_Result = TrainedModelLoading.MLPCountVector_result(
                str(review).strip())
            SVCTI_Result = TrainedModelLoading.SVCwithTFIDF_result(
                str(review).strip())
            MABTF_Result = TrainedModelLoading.MultinomialNBTFIDF_result(
                str(review).strip())
            return VADER_Result, NNB_Result, MNBC_Result, MPCC_Result, SVCTI_Result, MABTF_Result
        else:
            return "Sentiment analysis...", "Sentiment analysis...", "Sentiment analysis...", "Sentiment analysis...", "Sentiment analysis...", "Sentiment analysis..."
    else:
        return "Sentiment analysis...", "Sentiment analysis...", "Sentiment analysis...", "Sentiment analysis...", "Sentiment analysis...", "Sentiment analysis..."


# This the page title
content = html.Div(
    [
        dbc.Row
        ([
            dbc.Col(
                html.Img(src=app1.get_asset_url('Amazon_logo.png'),
                         className="log-image", width="200"),
                style={'textAlign': 'right'},
                width=3
            ),
            dbc.Col(
                html.H2('Headphones Reviews Analysis',
                        className="header-title",),
                width=9
            ),
        ]),
        html.Hr()
    ],
    className="content_style"
)

app1.layout = html.Div([content, list_group,], style={
                       'backgroundImage': 'url("/assets/background1.jpeg")'})

# run app. debug = True allows the server to refresh every time you update you code
if __name__ == "__main__":
    import os
    app1.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
