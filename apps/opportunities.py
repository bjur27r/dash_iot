import matplotlib.pyplot as plt
import os
#from data import clusterice
import numpy as np
import dash_html_components as html
from app import app, indicator, millify, df_to_table  # , sf_manager
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
from datetime import date


period = 'TX_OUT'
source = 'lifetime_d'
size_d = 'prob_1'


def cap(df, feature_name):
    min_value = df[feature_name].min()


def normalize(df, feature_name):
    result = df.copy()
    # for feature_name in df.columns:
    max_value = df[feature_name].max()
    min_value = df[feature_name].min()
    mean_value = df[feature_name].mean()
    df[feature_name] = df[feature_name].apply(lambda x: 3 * mean_value if x > 3 * mean_value else x)
    #  result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)

    return df[feature_name]


def features():
    a = pd.read_csv("/home/bjur/data/test.csv", sep="\t", encoding='utf8')
    list_c = a.columns.tolist()
    return list_c


def converted_opportunities(period, source, size_d, df):
    trace = go.Scatter(
        x=df[period],
        y=df[source],
        # z=df[size_d],
        text=df['prob_1'],
        mode='markers',
        # fillcolor=df["label_I"],

        name="converted opportunities",
        marker={
            'size': df[size_d] * 100  # tuple(),#normalize(df,size_d)*100#
            # 'size': normalize(df,size_d)
            # 'fill': df['label_I'],

            #  'line': {'width': 0.5, 'color': 'white'}
        },

    )

    data = [trace]

    layout = go.Layout(
        xaxis={'title': period},  # , 'type':'log'
        yaxis={'title': source},
        margin=dict(l=35, r=25, b=23, t=5, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


# returns heat map figure
def heat_map_fig(df, x, y):
    z = []
    for lead_type in y:
        z_row = []
        for stage in x:
            probability = df[(df["StageName"] == stage) & (df["Type"] == lead_type)][
                "Probability"
            ].mean()
            z_row.append(probability)
        z.append(z_row)

    trace = dict(
        type="heatmap", z=z, x=x, y=y, name="mean probability", colorscale="Blues"
    )
    layout = dict(
        margin=dict(t=25, l=210, b=85, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return go.Figure(data=[trace], layout=layout)


def df_to_plotly(df, d):
    return {'z': df, 'colorscale': "Blues", 'x': d, 'y': d}  # , 'layout':{'margin':{'t':250,'l':210,'b':85,'pad':4}}}


def heat_map_fig_3(df):
    df_cos = df
    # d = df_cos['label_I'].tolist()
    d = df_cos['cluster'].tolist()
    df_cos_2 = df_cos.drop(['cluster'], axis=1)
    cos_sim = cosine_similarity(df_cos_2)
    z = cos_sim  # .ravel()
    # x= df.columns.tolist()
    # d= df.index.tolist()
    print(z)
    # , x=d, y=d
    trace = dict(
        type="heatmap", z=z, name="mean probability", colorscale="Blues"
    )

    data2 = [dict(z=z, type='heatmap')]
    layout = dict(
        margin=dict(t=215, l=210, b=85, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    # return go.Figure(data=[trace], layout=layout)
    return go.Figure(
        data=go.Heatmap(df_to_plotly(cos_sim, d)))  # ,'layout':{'margin':{'t':250,'l':210,'b':85,'pad':4}}))


# returns top 5 lost opportunities
def top_open_opportunities(df):
    # df = df.sort_values("Amount", ascending=True)
    cols = ["CreatedDate", "Name", "Amount", "StageName"]
    df = df[cols].iloc[:5]
    df["Name"] = df["Name"].apply(lambda x: x[:30])  # only display 21 characters
    return df_to_table(df)


# returns top 5 lost opportunities
def top_lost_opportunities(df):
    df = df[df["StageName"] == "Closed Lost"]
    cols = ["CreatedDate", "Name", "Amount", "StageName"]
    df = df[cols].sort_values("Amount", ascending=False).iloc[:5]
    df["Name"] = df["Name"].apply(lambda x: x[:30])  # only display 21 characters
    return df_to_table(df)


# returns modal (hidden by default)
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
                                    "New Opportunity",
                                    style={
                                        "color": "#506784",
                                        "fontWeight": "bold",
                                        "fontSize": "20",
                                    },
                                ),
                                html.Span(
                                    "×",
                                    id="opportunities_modal_close",
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
                                # left div
                                html.Div(
                                    [
                                        html.P(
                                            ["Name"],
                                            style={
                                                "float": "left",
                                                "marginTop": "4",
                                                "marginBottom": "2",
                                            },
                                            className="row",
                                        ),
                                        dcc.Input(
                                            id="new_opportunity_name",
                                            placeholder="Name of the opportunity",
                                            type="text",
                                            value="",
                                            style={"width": "100%"},
                                        ),
                                        html.P(
                                            ["StageName"],
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_opportunity_stage",
                                            options=[
                                                {
                                                    "label": "Prospecting",
                                                    "value": "Prospecting",
                                                },
                                                {
                                                    "label": "Qualification",
                                                    "value": "Qualification",
                                                },
                                                {
                                                    "label": "Needs Analysis",
                                                    "value": "Needs Analysis",
                                                },
                                                {
                                                    "label": "Value Proposition",
                                                    "value": "Value Proposition",
                                                },
                                                {
                                                    "label": "Id. Decision Makers",
                                                    "value": "Closed",
                                                },
                                                {
                                                    "label": "Perception Analysis",
                                                    "value": "Perception Analysis",
                                                },
                                                {
                                                    "label": "Proposal/Price Quote",
                                                    "value": "Proposal/Price Quote",
                                                },
                                                {
                                                    "label": "Negotiation/Review",
                                                    "value": "Negotiation/Review",
                                                },
                                                {
                                                    "label": "Closed/Won",
                                                    "value": "Closed Won",
                                                },
                                                {
                                                    "label": "Closed/Lost",
                                                    "value": "Closed Lost",
                                                },
                                            ],
                                            clearable=False,
                                            value="Prospecting",
                                        ),
                                        html.P(
                                            "Source",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_opportunity_source",
                                            options=[
                                                {"label": "Web", "value": "Web"},
                                                {
                                                    "label": "Phone Inquiry",
                                                    "value": "Phone Inquiry",
                                                },
                                                {
                                                    "label": "Partner Referral",
                                                    "value": "Partner Referral",
                                                },
                                                {
                                                    "label": "Purchased List",
                                                    "value": "Purchased List",
                                                },
                                                {"label": "Other", "value": "Other"},
                                            ],
                                            value="Web",
                                        ),
                                        html.P(
                                            ["Close Date"],
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        html.Div(
                                            dcc.DatePickerSingle(
                                                id="new_opportunity_date",
                                                min_date_allowed=date.today(),
                                                # max_date_allowed=dt(2017, 9, 19),
                                                initial_visible_month=date.today(),
                                                date=date.today(),
                                            ),
                                            style={"textAlign": "left"},
                                        ),
                                    ],
                                    className="six columns",
                                    style={"paddingRight": "15"},
                                ),
                                # right div
                                html.Div(
                                    [
                                        html.P(
                                            "Type",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_opportunity_type",
                                            options=[
                                                {
                                                    "label": "Existing Customer - Replacement",
                                                    "value": "Existing Customer - Replacement",
                                                },
                                                {
                                                    "label": "New Customer",
                                                    "value": "New Customer",
                                                },
                                                {
                                                    "label": "Existing Customer - Upgrade",
                                                    "value": "Existing Customer - Upgrade",
                                                },
                                                {
                                                    "label": "Existing Customer - Downgrade",
                                                    "value": "Existing Customer - Downgrade",
                                                },
                                            ],
                                            value="New Customer",
                                        ),
                                        html.P(
                                            "Amount",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Input(
                                            id="new_opportunity_amount",
                                            placeholder="0",
                                            type="number",
                                            value="",
                                            style={"width": "100%"},
                                        ),
                                        html.P(
                                            "Probability",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Input(
                                            id="new_opportunity_probability",
                                            placeholder="0",
                                            type="number",
                                            max=100,
                                            step=1,
                                            value="",
                                            style={"width": "100%"},
                                        ),
                                    ],
                                    className="six columns",
                                    style={"paddingLeft": "15"},
                                ),
                            ],
                            className="row",
                            style={"paddingTop": "2%"},
                        ),
                        # submit button
                        html.P(
                            "note that this is just a demo application, and any new leads or opportunities you submit in this form will not be reflected.\nIn order to use the full functionality of the app, please clone the repository and place your own salesforce username, password, and API token into your environment variables.",
                        ),
                        html.Span(
                            "Submit",
                            id="submit_new_opportunity",
                            n_clicks=0,
                            className="button button--primary add",
                        ),
                    ],
                    className="modal-content",
                    style={"textAlign": "center"},
                )
            ],
            className="modal",
        ),
        id="opportunities_modal",
        style={"display": "none"},
    )


#names = list("opportunities_df3.columns")
layout = [
    # top controls
    html.Div(
        [
            html.Div(
                dcc.Dropdown(
                    id="converted_opportunities_dropdown",
                   # options=[{'label': name, 'value': name} for name in features()],
                     options=[
                        {"label": "By pepe", "value": "D"},
                        {"label": "By week", "value": "W-MON"},
                        {"label": "By month", "value": "M"},
                     ],
                    value="TX_OUT",
                    clearable=False,
                ),
                className="two columns",
                style={"marginBottom": "10", "marginTop": "20px", "marginBottom": "15px"},
            ),
            html.Div(
                dcc.Dropdown(
                    id="heatmap_dropdown",
           #         options=[{'label': name, 'value': name} for name in features()],
                     options=[
                        {"label": "All stages", "value": "all_s"},
                        {"label": "Cold stages", "value": "cold"},
                        {"label": "Warm stages", "value": "warm"},
                        {"label": "Hot stages", "value": "hot"},
                     ],
                    value="lifetime_d",
                    clearable=False,
                ),
                className="two columns",
                style={"marginBottom": "10", "marginTop": "20px", "marginBottom": "15px"},
            ),
            html.Div(
                dcc.Dropdown(
                    id="source_dropdown",
            #        options=[{'label': name, 'value': name} for name in features()],
                     options=[
                        {"label": "All sources", "value": "all_s"},
                        {"label": "Web", "value": "Web"},
                        {"label": "Word of Mouth", "value": "Word of mouth"},
                        {"label": "Phone Inquiry", "value": "Phone Inquiry"},
                        {"label": "Partner Referral", "value": "Partner Referral"},
                        {"label": "Purchased List", "value": "Purchased List"},
                        {"label": "Other", "value": "Other"},
                     ],
                    value="prob_1",
                    clearable=False,
                ),
                className="two columns",
                style={"marginBottom": "10", "marginTop": "20px", "marginBottom": "15px"},
            ),
            # add button
            html.Div(
                html.Span(
                    "Add new",
                    id="new_opportunity",
                    n_clicks=0,
                    className="button button--primary add",
                ),
                className="two columns",
                style={"float": "right"},
            ),
        ],
        className="row",
        style={"marginBottom": "10", "marginTop": "15px", "marginBottom": "15px"},
    ),
    # style={"marginTop": "5px", "marginBottom": "5px"}
    # indicators row
    html.Div(
        [
            indicator("#00cc96", "Sample Count", "left_opportunities_indicator"),
            indicator(
                "#119DFF", "Phising Sample", "middle_opportunities_indicator"
            ),
            indicator("#EF553B", "White Label", "right_opportunities_indicator"),
        ],
        className="row",
        style={"marginTop": "10px", "marginBottom": "10px"},
    ),
    # charts row div
    html.Div(
        [
            html.Div(
                [
                    html.P("Clusters 3M Comparisson"),
                    dcc.Graph(
                        id="converted_count",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="six columns chart_div",
            ),
            html.Div(
                [
                    html.P("Similarity Heatmap"),
                    dcc.Graph(
                        id="heatmap",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),

                ],
                className="six columns chart_div",
            ),
        ],
        className="row",
        style={"marginTop": "5px"},
    ),
    # tables row div
    html.Div(
        [
            html.Div(
                [
                    html.P(
                        "Population Behavioural Clusters",
                        style={
                            "color": "#808080",
                            "fontSize": "18px",
                            "textAlign": "center",
                            "marginBottom": "0",
                        },
                    ),
                    html.Div(
                        id="top_open_opportunities",
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
                        "Phising Sample Behavioural Clusters",
                        style={
                            "color": "#808080",
                            "fontSize": "18px",
                            "textAlign": "center",
                            "marginBottom": "0",
                        },
                    ),
                    html.Div(
                        id="top_lost_opportunities",
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
            modal(),
        ],
        className="row",
        style={"marginTop": "15px", "marginBottom": "15px"},  # "max height": "200px",
    ),
]


# updates heatmap figure based on dropdowns values or df updates
@app.callback(
    Output("heatmap", "figure"),
    [Input("opportunities_df3", "children")],
)
def heat_map_callback(df):
    df = pd.read_json(df, orient="split")

    return heat_map_fig_3(df)


# updates converted opportunity count graph based on dropdowns values or df updates
@app.callback(
    Output("converted_count", "figure"),
    [
        Input("converted_opportunities_dropdown", "value"),
        Input("heatmap_dropdown", "value"),
        Input("source_dropdown", "value"),
        Input("opportunities_df3", "children"),
    ],
)
def converted_opportunity_callback(period, source, size_d, df):
    df = pd.read_json(df, orient="split")
    df = round(df, 2)
    df['prob_1'] = df['prob_1'].astype(float)
    return converted_opportunities(period, source, size_d, df)


# updates left indicator value based on df updates
@app.callback(
    Output("left_opportunities_indicator", "children"),
    [Input("opportunities_df3", "children")],
)
def left_opportunities_indicator_callback(df):
    with open('/home/ubuntu/bjur27r-gmail.com/dash_app/data/sample_des.json') as json_file:
        data = json.load(json_file)
    return data['size_sample']


# updates middle indicator value based on df updates
@app.callback(
    Output("middle_opportunities_indicator", "children"),
    [Input("opportunities_df3", "children")],
)
def middle_opportunities_indicator_callback(df):
    with open('/home/ubuntu/bjur27r-gmail.com/dash_app/data/sample_des.json') as json_file:
        data = json.load(json_file)
    return data['size_phis']


# updates right indicator value based on df updates
@app.callback(
    Output("right_opportunities_indicator", "children"),
    [Input("opportunities_df3", "children")],
)
def right_opportunities_indicator_callback(df):
    df = pd.read_json(df, orient="split")
    lost = millify(str(df[(df["IsWon"] == 0) & (df["IsClosed"] == 1)]["Amount"].sum()))
    return lost


# hide/show modal
@app.callback(
    Output("opportunities_modal", "style"), [Input("new_opportunity", "n_clicks")]
)
def display_opportunities_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}


# reset to 0 add button n_clicks property
@app.callback(
    Output("new_opportunity", "n_clicks"),
    [
        Input("opportunities_modal_close", "n_clicks"),
        Input("submit_new_opportunity", "n_clicks"),
    ],
)
def close_modal_callback(n, n2):
    return 0


# add new opportunity to salesforce and stores new df in hidden div
@app.callback(
    Output("opportunities_df", "children"),
    [Input("submit_new_opportunity", "n_clicks")],
    [
        State("new_opportunity_name", "value"),
        State("new_opportunity_stage", "value"),
        State("new_opportunity_amount", "value"),
        State("new_opportunity_probability", "value"),
        State("new_opportunity_date", "date"),
        State("new_opportunity_type", "value"),
        State("new_opportunity_source", "value"),
        State("opportunities_df", "children"),
    ],
)
def add_opportunity_callback(
        n_clicks, name, stage, amount, probability, date, o_type, source, current_df
):
    if "DASH_PATH_ROUTING" in os.environ:
        return current_df

    if n_clicks > 0:
        if name == "":
            name = "Not named yet"
        query = {
            "Name": name,
            "StageName": stage,
            "Amount": amount,
            "Probability": probability,
            "CloseDate": date,
            "Type": o_type,
            "LeadSource": source,
        }

        sf_manager.add_opportunity(query)

        df = sf_manager.get_opportunities()

        return df.to_json(orient="split")

    return current_df


# updates top open opportunities based on df updates
@app.callback(
    Output("top_open_opportunities", "children"),
    [Input("opportunities_df3", "children")],
)
def top_open_opportunities_callback(df):
    df = pd.read_json(df, orient="split")
    # df_clust= clusterice(df,10)
    # df_clust.to_csv("c:\BC_DS\df_result_b.csv", sep = "\t", encoding='utf8')
    df['Cluster'] = df['cluster']
    df['Sample_Share(%)'] = round(df['cluster_Pob'] * 100, 0)
    df['Lifetime(days)'] = round(df['lifetime_d'], 0)
    df['Trans_In(x)'] = round(df['TX_IN'], 0)
    df['Trans_Out(x)'] = round(df['TX_OUT'], 0)
    df['Ratio_IN/OUT(x)'] = round(df['Trans_In(x)'] / df['Trans_Out(x)'], 2)
    df['Average_Value_In(USD)'] = round(df['value_IN'] / df['Trans_In(x)'], 0)
    df['Average_Value_Out(USD)'] = round(df['value_OUT'] / df['Trans_Out(x)'], 0)
    df['Phising Lookalike(%)'] = round(df['prob_1'] * 100, 0)
    df['balance_mean'] = round(df['TX_OUT'], 0)
    df_Out = df[['Cluster', 'Sample_Share(%)', 'Lifetime(days)', 'Trans_In(x)', 'Trans_Out(x)',
                 'Ratio_IN/OUT(x)', 'Average_Value_In(USD)', 'Average_Value_Out(USD)', 'Phising Lookalike(%)']]
    return df_to_table(df_Out)


# updates top lost opportunities based on df updates
@app.callback(
    Output("top_lost_opportunities", "children"),
    [Input("opportunities_df4", "children")],
)
def top_lost_opportunities_callback(df):
    df = pd.read_json(df, orient="split")
    # df_clust= clusterice(df,10)
    # df_clust.to_csv("c:\BC_DS\df_result_b.csv", sep = "\t", encoding='utf8')
    df['Cluster'] = df['cluster']
    df['Sample_Share(%)'] = round(df['cluster_Pob'] * 100, 0)
    df['Lifetime(days)'] = round(df['lifetime_d'], 0)
    df['Trans_In(x)'] = round(df['TX_IN'], 0)
    df['Trans_Out(x)'] = round(df['TX_OUT'], 0)
    df['Ratio_IN/OUT(x)'] = round(df['Trans_In(x)'] / df['Trans_Out(x)'], 2)
    df['Average_Value_In(USD)'] = round(df['value_IN'] / df['Trans_In(x)'], 0)
    df['Average_Value_Out(USD)'] = round(df['value_OUT'] / df['Trans_Out(x)'], 0)
    df['Phising Lookalike(%)'] = round(df['prob_1'] * 100, 0)
    df['balance_mean'] = round(df['TX_OUT'], 0)
    df_Out = df[['Cluster', 'Sample_Share(%)', 'Lifetime(days)', 'Trans_In(x)', 'Trans_Out(x)',
                 'Ratio_IN/OUT(x)', 'Average_Value_In(USD)', 'Average_Value_Out(USD)', 'Phising Lookalike(%)']]
    return df_to_table(df_Out)