import json
import math

import pandas as pd
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
import os
from colour import Color  # net
from datetime import datetime  # net
# from address_scor import adress_score
from address_scor import adress_score
import dash_daq as daq
from app import app, indicator, millify, df_to_table
import matplotlib.pyplot as plt


# from apps import network_graph
# , sf_manager


######################################################################################################################################################################
# styles: for right side hover/click component

####GLOBAL VARIABLES
YEAR = [2018, 2020]
LEVEL = [0, 20]
ACCOUNT = "0xe26cb453f146db2b6104e0b03125859d5d798a78"
L_COLOR = "level"



# returns pie chart that shows lead source repartition


layout = [
    #########################Title
    html.Div([html.H1("Satellite")],
             className="row",
             style={'textAlign': "center"}),
    #############################################################################################define the row
    html.Div(
        className="row",
        children=[
            ##############################################left side two input components
            html.Div(
                className="two columns",
                children=[
                    dcc.Markdown(d("""
                            **Time Range To Visualize**
                            Slide the bar to define year range.
                            """)),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.RangeSlider(
                                id='my-range-slider',
                                min=2017,
                                max=2020,
                                step=1,
                                value=[2017, 2020],
                                marks={

                                    2017: {'label': '2017'},
                                    2018: {'label': '2018'},
                                    2019: {'label': '2019'},
                                    2020: {'label': '2020'}
                                }
                            ),
                            html.Br(),
                            html.Div(id='output-container-range-slider'),

                            dcc.Markdown(d("""
                            **Crawling Level** To Visualize.
                            """)),
                            html.Br(),
                            html.Div(id='output-container-range-slider'),
                            dcc.RangeSlider(
                                id='my-level-slider',
                                min=0,
                                max=4,
                                step=1,
                                value=[0, 4],
                                marks={

                                    0: {'label': 'Level 0'},
                                    1: {'label': 'Level 1'},
                                    2: {'label': 'Level 2'},
                                    3: {'label': 'Level 3'},
                                    4: {'label': 'Level 4'}
                                }
                            ),
                            html.Br(),
                            html.Div(id='output-container-range-slider'),

                            html.Div(
                                className="twelve columns",
                                children=[
                                    dcc.Markdown(d("""
                            **Color Layer**
                            """)),
                                    dcc.RadioItems(
                                        options=[
                                            {'label': 'Level', 'value': 'level'},
                                            {'label': 'Risk', 'value': 'risk'},
                                            {'label': 'Cluster', 'value': 'cluster'}
                                        ],
                                        value='level',
                                        id='c_layer',
                                    ),
                                    html.Br(),
                                    html.Div(id='output-container-range-slider'),

                                    dcc.Markdown(d("""
                            **Flow** To Visualize.
                            """)),

                                    html.Div(id='output-container-range-slider'),
                                    dcc.RadioItems(
                                        options=[
                                            {'label': 'Inbound', 'value': 'Inb'},
                                            {'label': 'Outbound', 'value': 'Outb'}
                                        ],
                                        value='flow',
                                        id='f_layer',
                                    ),

                                    html.Br(),
                                    html.Div(id='output-container-range-slider'),

                                ]

                            ),

                        ],
                        style={'height': '500px'}
                    ),

                    ####

                    ####
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Markdown(d("""
                            **Account To Search**
                            Input the account to visualize.
                            """)),
                            dcc.Input(id="input1", type="text", placeholder="Address",
                                      value="0xe26cb453f146db2b6104e0b03125859d5d798a78"),
                            html.Div(id="output")
                        ],
                        style={'height': '200px'}
                    )
                ]
            ),

            ############################################middle graph component
            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="my-graph",
                                    figure=network_graph(YEAR, ACCOUNT, LEVEL, L_COLOR))],
            ),

            #########################################right side two output component
            html.Div(
                className="two columns",
                children=[
                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                            **Address Data**
                            Mouse over values in the graph.
                            """)),
                            html.Pre(id='hover-data', style=styles['pre'])
                        ],
                        style={'height': '400px'}),

                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                            **Click Data**
                            Click on points in the graph.
                            """)),
                            html.Pre(id='click-data', style=styles['pre'])
                        ],
                        style={'height': '400px'})
                ]
            )
        ]
    ),

    ####################
    # tables row div
    html.Div(
        [
            html.Div(
                [
                    html.P(
                        "Flows Description By Levels",
                        style={
                            "color": "#808080",
                            "fontSize": "20px",
                            "textAlign": "center",
                            "marginBottom": "0",
                        },
                    ),
                    html.Div(
                        id="inf_flows_table",
                        style={"padding": "0px 13px 5px 13px", "marginBottom": "5", "textAlign": "center"},
                    ),
                ],
                className="six columns",
                style={
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px",
                    "height": "100%",
                    "overflowY": "scroll",
                    "textAlign": "center",
                },
            ),
            html.Div(
                [
                    html.P(
                        "Address Description By Level",
                        style={
                            "color": "#808080",
                            "fontSize": "20px",
                            "textAlign": "center",
                            "marginBottom": "0",
                        },
                    ),
                    html.Div(
                        id="inf_nodes_table",
                        style={"padding": "0px 13px 5px 13px", "marginBottom": "5"},
                    ),
                ],
                className="six columns",
                style={
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px",
                    "height": "100%",
                    "overflowY": "scroll",
                },
            ),

        ],
    ),

    ######################

]


###################################callback for left side components
@app.callback(
    dash.dependencies.Output('my-graph', 'figure'),
    [dash.dependencies.Input('my-range-slider', 'value'), dash.dependencies.Input('input1', 'value'),
     dash.dependencies.Input('my-level-slider', 'value'), dash.dependencies.Input('c_layer', 'value')])
def update_output(value_1, input1, value_2, value_3):
    YEAR = value_1
    ACCOUNT = input1
    LEVEL = value_2
    L_COLOR = value_3
    return network_graph(value_1, input1, value_2, value_3)
    # to update the global variable of YEAR and ACCOUNT


################################callback for right side components
@app.callback(
    dash.dependencies.Output('hover-data', 'children'),
    [dash.dependencies.Input('my-graph', 'hoverData')])
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


@app.callback(
    dash.dependencies.Output('click-data', 'children'),
    [dash.dependencies.Input('my-graph', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData['points'], indent=2)


#####FLOW TABLES
# updates top open opportunities based on df updates
@app.callback(
    Output("inf_flows_table", "children"),
    [Input("opportunities_df3", "children")],
)
def top_open_opportunities_callback(df):
    edge1 = pd.read_csv('/home/ubuntu/bjur27r-gmail.com/model/upward.csv', sep="\t", encoding='utf8')
    edge1 = pd.read_csv('/home/ubuntu/bjur27r-gmail.com/model/upward.csv', sep="\t", encoding='utf8')
    df = edge1[['source', 'level', 'amount']].groupby(['source', 'level']).agg(
        sum_trans_adrs=pd.NamedAgg(column='amount', aggfunc='sum'),
        count_trans_adrs=pd.NamedAgg(column='amount', aggfunc='count'))
    df = df.reset_index()
    df = df[['level', 'count_trans_adrs', 'sum_trans_adrs']].groupby(['level']).agg(
        count_trans_adrs_levl=pd.NamedAgg(column='count_trans_adrs', aggfunc='count'),
        mean_trans_adrs_levl=pd.NamedAgg(column='count_trans_adrs', aggfunc='mean'),
        mean_trans_val_levl=pd.NamedAgg(column='sum_trans_adrs', aggfunc='mean'),
        sum_trans_val_levl=pd.NamedAgg(column='sum_trans_adrs', aggfunc='sum'))

    # count_trans_adrs_levl: numero de address distintos por nivel.
    # mean_trans_adrs_levl: transacciones medias de address.
    # mean_trans_val_levl : transaccion media por nivel
    # sum_trans_val_levl : suma todas las transacciones por nivel
    df = df.reset_index()
    df_2 = pd.DataFrame()
    df_2['Level'] = df['level']
    df_2['Distinct_Senders'] = round(df['count_trans_adrs_levl'], 1)
    df_2['Average_Trans'] = round(df['mean_trans_adrs_levl'], 1)
    df_2['Average_Trans_Value'] = round(df['mean_trans_val_levl'], 1)
    df_2['Total_Trans_Value'] = round(df['sum_trans_val_levl'], 1)
    return df_to_table(df_2)


# updates top open opportunities based on df updates
@app.callback(
    Output("inf_nodes_table", "children"),
    [Input("opportunities_df3", "children")],
)
def nodes_des(df):
    df_node_3 = df_nodes()
    df_nodes_out = df_node_3[['level', 'label', 'cluster', 'prob_1']].groupby(['level', 'label', 'cluster']).agg(
        LookAlike=pd.NamedAgg(column='prob_1', aggfunc='median'))

    df_nodes_out = df_nodes_out.reset_index()
    df_nodes_out['Level'] = df_nodes_out['level']
    df_nodes_out['LookAlike'] = round(df_nodes_out['LookAlike'] * 100, 1)
    df_nodes_out['Sannity Check'] = df_nodes_out['LookAlike'].apply(lambda x: 'SUSPICIOUS' if x > 50 else "OK")
    return df_to_table(df_nodes_out)

