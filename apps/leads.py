import json
import math
import requests
import pandas as pd
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
import os
#import networkx as nx  # net
from colour import Color  # net
from datetime import datetime  # net
from textwrap import dedent as d
#from address_scor import adress_score
import dash_daq as daq

#@source(models.py)
from apps.models import get_caudal
from app import app, indicator, millify, df_to_table
#from apps import network_graph
from influxdb_com import iot_db

# , sf_manager
adrs = 55525

a = requests.get("http://54.212.39.89/params")
data_plnt = a.json()
q_ref= data_plnt['q50']
cs_ref= data_plnt['csolar']
pot_ref= data_plnt['potencia_um']


# returns pie chart that shows lead source repartition
def pie_flow(df):
    trace = go.Pie(
        # labels=df['from'],
        labels=df['label'],
        values=df['tx'],
        hovertext="Label: " + df['label'],
        hole=.3
        # marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
    )

    layout = dict(margin=dict(l=15, r=10, t=0, b=65), legend=dict(orientation="h"))
    return dict(data=[trace], layout=layout)


def find_quartil(value, df, feature):
    print(value)

    print(df.iloc[4][feature])
    if value < df.iloc[4][feature]:
        return 1
    if value < df.iloc[5][feature]:
        return 2
    if value < df.iloc[6][feature]:
        return 3
    if value < df.iloc[7][feature]:
        return 4


def make_polar(df):
    scale = 1000000000000000000 / 180
    stats = pd.read_csv("/home/ubuntu/data/statistics_sample.csv", sep="\t", encoding='utf8')
    d3 = round(df['lifetime_d'].iloc[0], 0)
    # print(d3)
    life_p = find_quartil(d3, stats, 'lifetime_d')
    d3 = round(df['TX_OUT'].iloc[0] / df['TX_IN'].iloc[0], 0)
    rat_trans_p = find_quartil(d3, stats, 'rat_trans')
    d3 = round(df['TX_OUT'].iloc[0], 0)
    tx_out = find_quartil(d3, stats, 'TX_OUT')
    d3 = round(df['TX_IN'].iloc[0], 0)
    tx_in = find_quartil(d3, stats, 'TX_IN')
    df['value_IN'] = df['value_IN'] * scale
    d3 = round(df['value_IN'].iloc[0] / df['TX_IN'].iloc[0], 0)
    val_tx_in = find_quartil(d3, stats, 'VAL_TX_IN')
    df['value_OUT'] = df['value_OUT'] * scale
    d3 = round(df['value_OUT'].iloc[0] / df['TX_OUT'].iloc[0], 0)
    val_tx_out = find_quartil(d3, stats, 'VAL_TX_OUT')

    trace = go.Scatterpolar(
        r=[life_p, rat_trans_p, tx_out, tx_in, val_tx_in, val_tx_out],
        theta=['lifetime', 'Trains_In/Trans_Out', 'Trans_ins', 'Trans_Out', 'Average_Tiket_IN', 'Average_Tiket_Out'],
        fill='toself'
    )

    df = pd.read_csv("/home/ubuntu/bjur27r-gmail.com/dash_app/df_result_resume_withProb_scaled_phising.csv", sep="\t",
                     encoding='utf8')
    # df = df.iloc[-1]
    print(df)
    d3 = round(df['lifetime_d'].iloc[0], 0)
    # print(d3)
    life_p = find_quartil(d3, stats, 'lifetime_d')
    d3 = round(df['TX_OUT'].iloc[-1] / df['TX_IN'].iloc[0], 0)
    rat_trans_p = find_quartil(d3, stats, 'rat_trans')
    print(df['TX_OUT'].iloc[-1])
    d3 = round(df['TX_OUT'].iloc[-1], 0)
    tx_out = find_quartil(d3, stats, 'TX_OUT')
    d3 = round(df['TX_IN'].iloc[-1], 0)
    tx_in = find_quartil(d3, stats, 'TX_IN')
    df['value_IN'] = df['value_IN'] * scale
    d3 = round(df['value_IN'].iloc[-1] / df['TX_IN'].iloc[-1], 0)
    val_tx_in = find_quartil(d3, stats, 'VAL_TX_IN')
    df['value_OUT'] = df['value_OUT'] * scale
    d3 = round(df['value_OUT'].iloc[-1] / df['TX_OUT'].iloc[-1], 0)
    val_tx_out = find_quartil(d3, stats, 'VAL_TX_OUT')

    trace_2 = go.Scatterpolar(name="phising",
                              r=[life_p, rat_trans_p, tx_out, tx_in, val_tx_in, val_tx_out],
                              theta=['lifetime', 'Trains_In/Trans_Out', 'Trans_ins', 'Trans_Out', 'Average_Tiket_IN',
                                     'Average_Tiket_Out'],
                              fill='toself'
                              )

    layout = dict(
        radialaxis=dict(
            visible=True,
            range=[0, 5]
        )

    )

    #
    return dict(data=[trace, trace_2], layout=layout)


def time_serie(df):
    ##
    print(df)
    print("ENTRA")

    df["CreatedDate"] = pd.to_datetime(df["time"], unit='s')

    # df = (
    #    df.groupby([pd.Grouper(key="CreatedDate", freq='D'),pd.Grouper('flow')])['trans_value']
    #    .sum()
    #    .reset_index()
    #    .sort_values("CreatedDate")
    # )

    scale = 1000000000000000000 / 180
    df['trans_value'] = df['trans_value'].astype(float) / scale

    trace = [go.Scatter(

        x=df[df['flow'] == i]["CreatedDate"],
        y=df[df['flow'] == i]['trans_value'],  # /,
        mode='markers',
        opacity=0.8,
        marker={
            'size': 10,
            'line': {'width': 0.5, 'color': 'white'}
        },

        name=i
    ) for i in df['flow'].unique()]

    data = trace

    layout = go.Layout(
        xaxis=dict(showgrid=True),
        margin=dict(l=33, r=25, b=37, t=5, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


def time_serie_II(df, scale, frecc,value):
    #   df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s')
    df['timestamp'] = df['time'].astype('datetime64[ns]')

    df['value'] = df[value].astype(float) / scale


    df_b = (
        df.groupby([pd.Grouper(key="timestamp", freq=frecc)])['value']
            .sum()
            .reset_index()
            .sort_values("timestamp")
    )

    # go.Graph

    df = df_b.sort_values("timestamp")
    # trace = go.Scatter(
    trace = dict(
        type='line',
        x=df["timestamp"],
        y=df["value"],
        name="Value",

        fill="tozeroy",
        fillcolor="#e6f2ff",
    )

    data = [trace]

    layout = go.Layout(
        xaxis=dict(showgrid=True),
        margin=dict(l=33, r=25, b=37, t=5, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}
###########

def time_serie_III(df, scale, frecc,value):
    #   df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s')
    df['timestamp'] = df['fecha'].astype('datetime64[ns]')

    df['value'] = df[value].astype(float) / scale


    df_b = (
        df.groupby([pd.Grouper(key="timestamp", freq=frecc)])['value']
            .sum()
            .reset_index()
            .sort_values("timestamp")
    )

    # go.Graph

    df = df_b.sort_values("timestamp")
    # trace = go.Scatter(
    trace = dict(
        type='bar',
        x=df["timestamp"],
        y=df["value"],
        name="Value",

        fill="tozeroy",
        fillcolor="#e6f2ff",
    )

    data = [trace]

    layout = go.Layout(
        xaxis=dict(showgrid=True),
        margin=dict(l=33, r=25, b=37, t=5, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


##############3
def converted_leads_count(period, df):
    df["CreatedDate"] = pd.to_datetime(df["CreatedDate"], format="%Y-%m-%d")
    df = df[df["Status"] == "Closed - Converted"]

    df = (
        df.groupby([pd.Grouper(key="CreatedDate", freq=period)])
            .count()
            .reset_index()
            .sort_values("CreatedDate")
    )

    trace = go.Scatter(
        x=df["CreatedDate"],
        y=df["Id"],
        name="converted leads",
        fill="tozeroy",
        fillcolor="#e6f2ff",
    )

    data = [trace]

    layout = go.Layout(
        xaxis=dict(showgrid=False),
        margin=dict(l=33, r=25, b=37, t=5, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


def modal():
    return html.Div(
        html.Div(
            [
                html.Div(
                    [

                        # modal header
                        html.Div(
                            [
                                html.Span(
                                    "Parametros de  Planta",
                                    style={
                                        "color": "#506784",
                                        "fontWeight": "bold",
                                        "fontSize": "20",
                                    },
                                ),
                                html.Span(
                                    "×",
                                    id="leads_modal_close",
                                    n_clicks=0,
                                    style={
                                        "float": "right",
                                        "cursor": "pointer",
                                        "marginTop": "0",
                                        "marginBottom": "17",
                                    },
                                ),
                            ],
                            className="row",
                            style={"borderBottom": "1px solid #C8D4E3"},
                        ),

                        # modal form
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Gradiente Maximo[l/m]",

                                    ],
                                    style={
                                        "float": "left",
                                        "marginTop": "4",
                                        "marginBottom": "2",
                                    },
                                    className="row",
                                ),
                                dcc.Input(
                                    id="grad_max",
                                    # placeholder="Enter company name",
                                    type="float",
                                    value=21.0,
                                    style={"width": "100%"},
                                ),


                                ############
                                html.P(
                                    [
                                        "Potencia Bomba (kW)",

                                    ],
                                    style={
                                        "float": "left",
                                        "marginTop": "4",
                                        "marginBottom": "2",
                                    },
                                    className="row",
                                ),
                                dcc.Input(
                                    id="pot_nom",
                                    # placeholder="Enter company name",
                                    type="float",
                                    value=4.0,
                                    style={"width": "100%"},
                                ),

                                    #####################
                                ############
                                html.P(
                                    [
                                        "Potencia umbral de trabajo (kW)",

                                    ],
                                    style={
                                        "float": "left",
                                        "marginTop": "3",
                                        "marginBottom": "2",
                                    },
                                    className="row",
                                ),
                                dcc.Input(
                                    id="pot_thres",
                                    # placeholder="Enter company name",
                                    type="float",
                                    value=3.0,
                                    style={"width": "100%"},
                                ),

                                #####################

                                ############
                                html.P(
                                    [
                                        "Punto de Trabajo MCA-Si es necesario",

                                    ],
                                    style={
                                        "float": "left",
                                        "marginTop": "4",
                                        "marginBottom": "2",
                                    },
                                    className="row",
                                ),
                                dcc.Input(
                                    id="alt_trabj",
                                    # placeholder="Enter company name",
                                    type="float",
                                    value=300.0,
                                    style={"width": "100%"},
                                ),

                             #####################
                                ############
                                html.P(
                                    [
                                        "Campo Solar",

                                    ],
                                    style={
                                        "float": "left",
                                        "marginTop": "4",
                                        "marginBottom": "2",
                                    },
                                    className="row",
                                ),
                                dcc.Input(
                                    id="csolar",
                                    # placeholder="Enter company name",
                                    type="float",
                                    value=12,
                                    style={"width": "100%"},
                                ),

                                #####################
                                ############
                                html.P(
                                    [
                                        "Ubicacion (Long/Lat)-Si es necesario",

                                    ],
                                    style={
                                        "float": "left",
                                        "marginTop": "4",
                                        "marginBottom": "2",
                                    },
                                    className="row",
                                ),
                                dcc.Input(
                                    id="coord",
                                    # placeholder="Enter company name",
                                    type="float",
                                    value="",
                                    style={"width": "100%"},
                                ),

                                #####################

                                ############
                                html.P(
                                    [
                                        "Tamaño Sector(Ha)",

                                    ],
                                    style={
                                        "float": "left",
                                        "marginTop": "4",
                                        "marginBottom": "2",
                                    },
                                    className="row",
                                ),
                                dcc.Input(
                                    id="super",
                                    # placeholder="Enter company name",
                                    type="float",
                                    value="",
                                    style={"width": "100%"},
                                ),

                                #####################






                            ],
                            className="row",
                            style={"padding": "2% 8%"},
                        ),

                        # submit button
                        html.P(
                            "Todos los parametros seran persistidos, para cualquier alteración vuelva a rellenar este formulario",
                        ),
                        html.Span(
                            "Guardar",
                            id="submit_planta",
                            n_clicks=0,
                            className="button button--primary add"
                        ),
                    ],
                    className="modal-content",
                    style={"textAlign": "center"},
                )
            ],
            className="modal",
        ),
        id="leads_modal",
        style={"display": "none"},
    )


layout = [

    # top controls
    html.Div(
        [
                    html.Div([
                        dcc.Interval(id='interval1', interval=5*1000, n_intervals=0),
                        html.H1(id='label1', children='')
                    ]),
            # add button

            html.Div(
                [html.H3("Explotacion",
                         style={"margin-bottom": "5px", "margin-top": "5px", "color": "Navy blue",
                                "font-family": "Arial"},
                         ),
                 html.P(id="adrs_indicator",
                        children=["init"], style={"margin-bottom": "5px", "margin-top": "5px", "color": "grey"}),

                 html.P(id="stateB",
                        children=["init"], style={"margin-bottom": "5px", "margin-top": "5px", "color": "grey"})

                 ]),
            #  indicator(
            #  "#00cc96", "Address","adrs_indicator"

            # ),

             html.Div([
            html.Span(
                "STOP",
                id="stop",
                n_clicks=0,
                className="button button--primary",
                style={
                    "height": "34",
                    "background": "#119DFF",
                    "border": "2px solid #119DFF",
                    "color": "white",
                    "marginBottom": "10",
                    "marginTop": "15",
                    "float": "right"
                },
            ),

html.Span(
                "RUN",
                id="start",
                n_clicks=0,
                className="button button--primary",
                style={
                    "height": "34",
                    "background": "#119DFF",
                    "border": "2px solid #119DFF",
                    "color": "white",
                    "marginBottom": "10",
                    "marginTop": "15",
                    "float": "right"
                },
            ),


            html.Span(
                "Parametros Planta",
                id="new_lead",
                n_clicks=0,
                className="button button--primary",
                style={
                    "height": "64",
                    "background": "#119DFF",
                    "border": "5px ",
                    "color": "white",
                    "marginBottom": "10",
                    "marginTop": "15",
                    "float": "left"
                },
            ),

                 ],
                 className="four-columns row",
                 style={
                     "marginTop": "20",
                     "marginBottom": "10",
                     "float": "right"},

             ),
            #        className="two columns",
            #        style={"marginTop": "20", "marginBottom": "10", "float": "right"},
            #    ),
        ],
        className="row",
        style={
            "marginTop": "20",
            "marginBottom": "10"},
    ),


    ###############
# table div

    html.Div(
        [html.H3("Metricas de Trabajo Instantaneas",
                 style={"margin-bottom": "10px", "margin-top": "10px"},
                 ),
         html.Div(
             [
                 html.Div([
                     html.Div(
                         daq.Gauge(
                             id="metric_risk_1",
                             label='Potencia Generada',
                             color="#0074e4",
                             scale={'start': 0, 'interval': 5, 'labelInterval': 20},
                             value=0,
                             showCurrentValue=True,
                             units="kW",
                             min=0,
                             max=cs_ref,
                         ), className="four columns chart_div"

                     ),
                     html.Div(
                         daq.Gauge(
                             id="metric_risk_2",
                             label='Potencia Consumida',
                             color="#0074e4",
                             scale={'start': 0, 'interval': 5, 'labelInterval': 20},
                             value=0,
                             showCurrentValue=True,
                             units="kW",
                             min=0,
                             max=round(pot_ref*1.1,0),
                         ), className="four columns chart_div"),

                     html.Div(
                         daq.Gauge(
                             id="metric_risk_3",
                             label='Caudal Extraido',
                             color="#0074e4",
                             scale={'start': 0, 'interval': 3, 'labelInterval': 2},
                             value=0,
                             showCurrentValue=True,
                             units="M3",
                             min=0,
                             max=round(q_ref*1.3),
                         ), className="four columns chart_div"),

                 ], className="row")

             ],

         ),

         ]),  # End Div

    ############



    ##################



    # indicators row div

    html.Div(
        [
            html.Div(
                [

                    html.Div(
                        [
                            html.H3("Metricas Explotacion",
                                    style={"margin-bottom": "10px", "margin-top": "10px"},
                                    ),
                            html.Div(
                                [
                                    indicator(
                                        "#00cc96", "Potencia Generada (kW)", "metric_1"
                                    ),
                                    indicator(
                                        "#119DFF", "Potencia Consumida (kW)", "metric_2"
                                    ),
                                    indicator(
                                        "#EF553B",
                                        "Frecuencia (HZ)",
                                        "metric_3",
                                    ),
                                ],
                                className="row",
                            ),

                            html.Div(
                                [
                                    indicator(
                                        "#00cc96", "Caudal Instantaneo (m3/min)", "metric_4"
                                    ),
                                    indicator(
                                        "#00cc96", "Caudal Instantaneo (m3/Hora)", "metric_5"
                                    ),
                                    indicator(
                                        "#00cc96", "Caudal Esperado (m3/Hoy)", "metric_6"
                                    ),

                                ],
                                className="row",

                            ),

                            html.Div(
                                [

                                    indicator(
                                        "#119DFF", "Acumulado Dia M3", "metric_7"
                                    ),
                                    indicator(
                                        "#119DFF", "Acumulado Semana M3", "metric_8"
                                    ),
                                    indicator(
                                        "#EF553B",
                                        "Acumulado Mes M3",
                                        "metric_9",
                                    ),
                                ],
                                className="row",
                            ),
                        ],
                        className="eight columns"
                    ),
                ]),
                    ###
                    html.Div(

                        # 'color':'grey','fontSize': '18px',
                        [
                            html.H3("Punto Trabajo de La Bomba", style={"margin-bottom": "10px", "margin-top": "10px"}),
                            html.Div([
                                dcc.Graph(
                                    id="polar_me",
                                    style={"height": "90%", "width": "98%"},
                                    config=dict(displayModeBar=False),
                                ),
                            ], )
                        ],

                        className="four columns"  # chart_div"
                    ),

                ],
                className="row"
            ),

            ###
            # charts row div
            html.Div([
                html.H3("Produccion Historica Agua",
                        style={"margin-bottom": "10px", "margin-top": "10px"},
                        ),
            ]),

            ################

            html.Div(
                [

                    html.Div(
                        [

                            html.P(
                        "Potencia",
                        style={
                            "textAlign": "left",
                            "marginBottom": "2",
                            "marginTop": "4",
                        },
                    ),
                    dcc.Dropdown(
                        id="metrics_inst",
                        options=[
                            {"label": "Energia Producida",
                             "value": "gen"},
                            {
                                "label": "Potencia Consumida",
                                "value": "pot_en",
                            },
                            {
                                "label": "Caudal Entregado",
                                "value": "q_en",
                            },

                        ],
                        value="q_en",
                    ),
                        ],
                        className="six columns"
                    ),
                    html.Div(
                        [
                            html.P(
                                "Produccion Caudal",
                                style={
                                    "textAlign": "left",
                                    "marginBottom": "2",
                                    "marginTop": "4",
                                },
                            ),

dcc.Dropdown(
                        id="caudl-sources",
                        options=[
                            {"label": "Caudal Aportado(M3)",
                             "value": "q_en"},
                            {
                                "label": "Pluviometeria(M3)",
                                "value": "pluvi",
                            },
                            {
                                "label": "Total(M3)",
                                "value": "Qtotal",
                            },
                            {
                                "label": "Precipitación(l/m2)",
                                "value": "prec",
                            },
                            {
                                "label": "Temperatura Media(ºc)",
                                "value": "tmed",
                            },
                            {
                                "label": "Sol",
                                "value": "sol",
                            },

                            {
                                "label": "Presion",
                                "value": "presMax",
                            },

                        ],
                        value="Qtotal",
                    ),



                        ],
                        className="six columns"
                    ),

                     ],
                className="row",
                style={"marginTop": "10","margin-bottom": "5px"},
            ),
##Second dropdown
    html.Div(
        [

            html.Div(
                [

                    html.P(
                        "Periodo",
                        style={
                            "textAlign": "left",
                            "marginBottom": "2",
                            "marginTop": "4",
                        },
                    ),
                    dcc.Dropdown(
                        id="period_b",
                        options=[
                            {"label": "Horario", "value": "H"},
                            {"label": "Diario", "value": "D"},
                            {"label": "Semanal", "value": "W-MON"},
                            {"label": "Mensual", "value": "M"},
                        ],
                        value="D",
                        clearable=False,
                    ),
                ],
                className="six columns"
            ),
            html.Div(
                [

                    html.P(
                        "Periodo",
                        style={
                            "textAlign": "left",
                            "marginBottom": "2",
                            "marginTop": "4",
                        },
                    ),
                    dcc.Dropdown(
                        id="period_bQ",
                        options=[

                            {"label": "Dario", "value": "D"},
                            {"label": "Semanal", "value": "W-MON"},
                            {"label": "Mensual", "value": "M"},
                        ],
                        value="D",
                        clearable=False,
                    ),
                ],
                className="six columns"
            ),

        ],
        className="row",
        style={"marginTop": "10", "margin-bottom": "5px"},
    ),







                    ###########3
            html.Div(
                [

                    html.Div(
                        [



                            html.P("Potencia", style={'color': 'grey', 'fontSize': '18px'}),
                            dcc.Graph(
                                id="potencia",
                                style={"height": "90%", "width": "98%"},
                                config=dict(displayModeBar=False),
                            ),
                        ],
                        className="six columns chart_div"
                    ),

                    html.Div(
                        [
                            html.P("Caudal Aportado/Pluviometria", style={'color': 'grey', 'fontSize': '18px'}),
                            dcc.Graph(
                                id="Qtrans",
                                style={"height": "90%", "width": "98%"},
                                config=dict(displayModeBar=False),
                            ),
                        ],
                        className="six columns chart_div"
                    ),

                ],
                className="row",
                style={"marginTop": "5"},
            ),
       # Div


    html.H3("First Level Flows",
            style={"margin-bottom": "10px", "margin-top": "10px"},
            ),

    html.Div(
        [
            html.Div(
                [
                    html.P("Inbound Transaction First Level"),
                    dcc.Graph(
                        id="intrans_1",
                        style={"height": "95%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="six columns chart_div"
            ),

            html.Div(
                [
                    html.P("Outbound Transaction First Level"),
                    dcc.Graph(
                        id="outrans_2",
                        style={"height": "95%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="six columns chart_div"
            ),

        ],
        className="row",
        style={"marginTop": "5"},
    ),

    ###############
    modal(),
]


# updates left indicator based on df updates
# @app.callback(
#    Output("rawind", "children"), [Input("new_lead_company", "value")])
# def rawind_callback(adrs):
#    sdr = adress_score(adrs)
#    df, raw = sdr.ind_data()
#   df = pd.read_json(df, orient="split")
#    return df.to_json(orient="split")

@app.callback(
    [Output("metric_1", "children"), Output("metric_risk_1", "value"),Output("metric_2", "children"), Output("metric_risk_2", "value"), Output("metric_3", "children"), Output("metric_4", "children"), Output("metric_risk_3", "value")]
    , [Input('interval1', 'n_intervals')]  # [Input("rawind", "children")]
)

def instant_metrics(n):
    d1 = 3
    clientB = iot_db('54.212.39.89', "admin", "Carrion2017", 'tempDB')
    print(n)
    with open('stations.txt') as json_file:
        data_st = json.load(json_file)
    volt_pv = clientB.get_last('voltage_PV')*data_st['csolar']/(360*1.5)
    olt_pv = clientB.get_last('outPower')/1000000
    ofrec = clientB.get_last('ofreq')/100
    caudal = clientB.get_last('caudal')
    d2 = round(volt_pv, 0)
    frec = round(ofrec, 0)
    d3 = d2
    #clientB = iot_db('54.212.39.89', "admin", "Carrion2017", 'tempDB')
    print(olt_pv)
    #d3 = 3#round(df['lifetime_d'], 0)
    #d4 = 3#df['label']
    #d5 = 3#round(df['TX_IN'], 0)
    #d6 = 3#round(len(raw[raw['flow'] == 'IN']['from'].unique()), 0)
    #g1 = 3#len(raw[raw['flow'] == 'IN']['from'].unique()) * scale
    #d7 = 3#round((raw[raw['flow'] == 'IN']['trans_value'].sum()) / g1, 2)
    #d8 = 3#round(df['TX_OUT'], 0)
    #d9 = 3#round(len(raw[raw['flow'] == 'OUT']['to'].unique()), 0)
    #g2 = 3#len(raw[raw['flow'] == 'OUT']['to'].unique()) * scale
    #d10 = 3#round((raw[raw['flow'] == 'OUT']['trans_value'].sum()) / g2, 2)
    #d11 = 3#round(df['prob_1'] * 100)
    #d12 = 3#round(df['prob_0'] * 100)

    ##Serie


    #in_trans = 3#time_serie(raw)
    #pol = 3#make_polar(df)

    from datetime import date

    #raw["time_s"] = pd.to_datetime(raw["time"], unit='s')
    #raw = raw.sort_values("time_s")
    #last_tx = raw.iloc[-1]["time_s"].strftime("%d/%m/%Y")
    #last_ts = raw.iloc[-1]["time"]  #
    #today = date.today()
    #delta = today - date.fromtimestamp(last_ts)
    #if delta.days > 30:
    #    status = "INACTIVE"
    #else:
    #    status = "ACTIVE"

    #state = status + "- Last time active: " + str(last_tx)

    return d2, d3, olt_pv, olt_pv , frec,caudal, caudal#, state, d2, d3, d4, d5, d6, d7, d8, d9, d10, out_trans, in_trans, int(d11), int(d12), pol




@app.callback(
    Output("potencia", "figure"),
    [Input("metrics_inst", "value"), Input("period_b", "value")],
)

def map_callback(value,per):
    clientB = iot_db('54.212.39.89', "admin", "Carrion2017", 'tempDB')
    id_2='4386B'
#    df_ts = clientB.get_serie(value)  #
#    df_ts = df_ts.rename(columns={0: 'timestamp', 1: 'value'})
    filename = "/home/bjur/PycharmProjects/invter_app/venv/data/" + id_2 + "sim"
    #dff.to_csv
    df_ts = pd.read_csv(filename, sep=",")

    serie1 = time_serie_II(df_ts, 1, per,value)


    return serie1

############Caudales
@app.callback(
    Output("Qtrans", "figure"),
    [Input("caudl-sources", "value"), Input("period_bQ", "value")])


def mapQ_callback(value,per):
    id_2='4358X'
#    df_ts = clientB.get_serie(value)  #
#    df_ts = df_ts.rename(columns={0: 'timestamp', 1: 'value'})
    filenameb = "/home/bjur/PycharmProjects/invter_app/venv/data/" + id_2 + "daily_merged"
    print(filenameb)
    #dff.to_csv
    df_tsB = pd.read_csv(filenameb, sep=";")
    print(df_tsB.columns)
    df_tsB['pluvi']=df_tsB['prec']*50
    #Qtotal
    df_tsB['Qtotal']= df_tsB['pluvi'].astype(float)+ df_tsB['q_en'].astype(float)
    serie1 = time_serie_III(df_tsB, 1, per,value)


    return serie1


############






# updates middle indicator based on df updates
@app.callback(
    Output("intrans_1", "figure"), [Input("rawind", "children")]
)
def middle_leads_indicator_callback(df):
    # sdr = adress_score(adrs)
    # df, raw = sdr.ind_data()
    df = pd.read_csv("/home/ubuntu/bjur27r-gmail.com/model/sample_1l.csv", sep=';', encoding='utf-8')
    df_out = df[df['flow'] == 'IN']

    return pie_flow(df_out)


# updates middle indicator based on df updates
@app.callback(
    Output("outrans_2", "figure"), [Input("rawind", "children")]
)
def middle_leads_indicator_callback(df):
    # sdr = adress_score(adrs)
    # df, raw = sdr.ind_data()
    df = pd.read_csv("/home/ubuntu/bjur27r-gmail.com/model/sample_1l.csv", sep=';', encoding='utf-8')
    df_out = df[df['flow'] == 'OUT']

    return pie_flow(df_out)


# updates middle indicator based on df updates
@app.callback(
    Output("middle_leads_indicator", "children"), [Input("rawind", "children")]
)
def middle_leads_indicator_callback(df):
    df = pd.read_json(df, orient="split")
    return open_leads


# updates right indicator based on df updates
@app.callback(
    Output("right_leads_indicator", "children"), [Input("leads_df", "children")]
)
def right_leads_indicator_callback(df):
    df = pd.read_json(df, orient="split")
    converted_leads = len(df[df["Status"] == "Closed - Converted"].index)
    lost_leads = len(df[df["Status"] == "Closed - Not Converted"].index)
    conversion_rates = converted_leads / (converted_leads + lost_leads) * 100
    conversion_rates = "%.2f" % conversion_rates + "%"
    return conversion_rates


# update pie chart figure based on dropdown's value and df updates
@app.callback(
    Output("lead_source", "figure"),
    [Input("lead_source_dropdown", "value"), Input("leads_df", "children")],
)
def lead_source_callback(status, df):
    df = pd.read_json(df, orient="split")
    return lead_source(status, df)


# update table based on dropdown's value and df updates
@app.callback(
    Output("leads_table", "children"),
    [Input("lead_source_dropdown", "value"), Input("leads_df", "children")],
)
def leads_table_callback(status, df):
    df = pd.read_json(df, orient="split")
    if status == "open":
        df = df[
            (df["Status"] == "Open - Not Contacted")
            | (df["Status"] == "Working - Contacted")
            ]
    elif status == "converted":
        df = df[df["Status"] == "Closed - Converted"]
    elif status == "lost":
        df = df[df["Status"] == "Closed - Not Converted"]
    df = df[["CreatedDate", "Status", "Company", "State", "LeadSource"]]
    return df_to_table(df)


# update pie chart figure based on dropdown's value and df updates
@app.callback(
    Output("converted_leads", "figure"),
    [Input("converted_leads_dropdown", "value"), Input("leads_df", "children")],
)
def converted_leads_callback(period, df):
    df = pd.read_json(df, orient="split")
    return converted_leads_count(period, df)


# hide/show modal
@app.callback(Output("leads_modal", "style"), [Input("new_lead", "n_clicks")])
def display_leads_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}


@app.callback([Output("stop", "style")], [Input("stop", "n_clicks")])
def stop_callback(n):
    with open('stations.txt') as json_file:
        data_st = json.load(json_file)
    data = data_st
    data['state'] = 5
    with open('stations.txt', 'w') as outfile:
        json.dump(data, outfile)

    a = requests.get("http://54.212.39.89/stop")

    return  0

@app.callback([Output("start", "style"),Output("stateB","children")], [Input("start", "n_clicks")])
def start_callback(n):
    with open('stations.txt') as json_file:
        data_st = json.load(json_file)
    data = data_st
    data['state'] = 1
    with open('stations.txt', 'w') as outfile:
        json.dump(data, outfile)

    a = requests.get("http://54.212.39.89/start")
    return  0, "Running"


# reset to 0 add button n_clicks property
@app.callback(
    Output("new_lead", "n_clicks"),
    [Input("leads_modal_close", "n_clicks"), Input("submit_planta", "n_clicks"),Input("csolar","value"),Input("alt_trabj","value"),Input("grad_max","value"),Input("pot_nom","value"),Input("pot_thres","value",)],
)
def close_modal_callback(n, n2,csol,alt,grad,potnm,pot_um):
    pram_ply = {}
    pram_ply['csolar']=csol
    pram_ply['plant']="532D"
    pram_ply['alt']=alt
    pram_ply['pot'] = potnm
    pram_ply['grad']=grad
    pram_ply['pot_um'] = pot_um
    q = get_caudal(pram_ply['grad'],pram_ply['alt'],pram_ply['pot'])
    pram_ply['q50']=float(q)
    with open('stations.txt', 'w') as outfile:
        json.dump(pram_ply, outfile)

    return 0


# add new lead to salesforce and stores new df in hidden div
@app.callback(
    Output("leads_df", "children"),
    [Input("submit_new_lead", "n_clicks")],
    [
        State("new_lead_status", "value"),
        State("new_lead_state", "value"),
        State("new_lead_company", "value"),
        State("new_lead_source", "value"),
        State("leads_df", "children"),
    ],
)
def add_lead_callback(n_clicks, status, state, company, source, current_df):
    if "DASH_PATH_ROUTING" in os.environ:
        return current_df
    if n_clicks > 0:
        if company == "":
            company = "Not named yet"
        query = {
            "LastName": company,
            "Company": company,
            "Status": status,
            "State": state,
            "LeadSource": source,
        }
        sf_manager.add_lead(query)
        df = sf_manager.get_leads()
        return df.to_json(orient="split")

    return current_df
