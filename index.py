## -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import flask
#import plotly.plotly as py
import chart_studio.plotly as py
from plotly import graph_objs as go
import math
from app import app, server#, sf_manager
from apps import  leads,opportunities# ,network,,
#import dash_auth




# Keep this out of source code repository - save in a file or a database
#VALID_USERNAME_PASSWORD_PAIRS = {
#    'hello': 'world'
#}

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#auth = dash_auth.BasicAuth(
#    app,
#    VALID_USERNAME_PASSWORD_PAIRS
#)
#http://54.212.39.89/start

application = app.server
app.layout = html.Div(
    [
        # header
        html.Div([

            html.Span("XXXXXXX[V01]", className='app-title'),

            html.Div(
                html.Img(src=app.get_asset_url('logo_3.png'),height="100%")
                ,style={"float":"right","height":"100%"})
            ],
            className="row header",
            style={"BackColor": "dodgerblue"}
            ),

        # tabs
        html.Div([

            dcc.Tabs(
                id="tabs",
                style={"height":"20","verticalAlign":"middle","fontSize": "25px","marginTop": "2px", "marginBottom": "2px"},
                children=[
                    dcc.Tab(label="Prevision Meteo", value="opportunities_tab"),
                    dcc.Tab(label="Monitorizacion", value="leads_tab"),
                    dcc.Tab(id="cases_tab",label="Satelite", value="cases_tab"),
                ],
                value="leads_tab",
            )

            ],
            className="row tabs_div",
           # style={"marginTop": "5px", "marginBottom": "5px"},

            ),


        # divs that save dataframe for each tab
     #   html.Div(
       #         sf_manager.get_opportunities().to_json(orient="split"),  # opportunities df
                    #file_path = "c:\BC_DS\df_result_toclust.csv",
                    #pd.read_csv("/home/ubuntu/data/df_result_toclustV2_withProb.csv", sep = "\t", encoding='utf8').to_json(orient="split"),
            #    id="opportunities_df2",
            #    style={"display": "none"},
            #),
            html.Div(
       #         sf_manager.get_opportunities().to_json(orient="split"),  # opportunities df
                    #file_path = "c:\BC_DS\df_result_toclust.csv",
                    pd.read_csv("/home/bjur/data/test.csv", sep = "\t", encoding='utf8').to_json(orient="split"),
                id="opportunities_df3",
                style={"display": "none"},
            ),
          html.Div(
                            pd.read_csv("/home/bjur/data/test.csv", sep = "\t", encoding='utf8').to_json(orient="split"),
                id="opportunities_df4",
                style={"display": "none"},
            ),

       #     html.Div( pd.read_csv("/home/ubuntu/bjur27r-gmail.com/dash_app/sample_ind.csv", sep = "\t",encoding='utf8').to_json(orient="split"), id="rawind", style={"display": "none"}),
       # html.Div( pd.read_csv("/home/ubuntu/bjur27r-gmail.com/dash_app/raw_ind.csv", sep = "\t",encoding='utf8').to_json(orient="split"), id="rawind2", style={"display": "none"}),

        # leads df
        #html.Div(sf_manager.get_cases().to_json(orient="split"), id="cases_df", style={"display": "none"}), # cases df



        # Tab content
        html.Div(id="tab_content", className="row", style={"margin": "2% 3%","marginTop": "60px", "marginBottom": "15px"}),

        html.Link(href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/amadoukane96/8a8cfdac5d2cecad866952c52a70a50e/raw/cd5a9bf0b30856f4fc7e3812162c74bfc0ebe011/dash_crm.css", rel="stylesheet")
    ],
    className="row",
    style={"margin": "0%","marginTop": "5px", "marginBottom": "5px"},
)


@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "opportunities_tab":
        return opportunities.layout
    elif tab == "cases_tab":
        return network.layout
    elif tab == "leads_tab":
        return leads.layout
    else:
        return opportunities.layout

if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server..."
           "please wait until server has fully started"))

    # Run app
    application.run(host="0.0.0.0", port=8051)