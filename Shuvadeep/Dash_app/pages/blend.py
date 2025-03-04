import dash
from dash import dcc, html, dash_table, Input, Output, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine
CONN_STRING = "postgresql+psycopg2://brioadmin:Gbsm%401234@briopgdb.postgres.database.azure.com:5432/gmr"

def get_data(query):
    # create a connection to the database
    engine = create_engine(CONN_STRING)
    data = pd.read_sql(query, engine)
    return data

data_pile_summary = get_data("SELECT * FROM cyms.pile_summary")
# Function to compute quantity using if-else condition
def compute_quantity(row):
    if row["TOP QNTY"] > 1000:
        return row["TOP QNTY"]
    else:
        return row["TOP QNTY"] + row["BOTTOM QNTY"]

data_pile_summary["Quantity top"] = data_pile_summary.apply(lambda row: compute_quantity(row), axis=1)
# Function to compute GCV using if-else condition
def compute_gcv(row):
    if row["TOP QNTY"] > 1000:
        return row["TOP GCV"]
    else:
        return row["PILE WTD GCV"]

data_pile_summary ["GCV top"] = data_pile_summary .apply(lambda row: compute_gcv(row), axis=1)
# selecting desired columns from the dataframe
pile_summary_cleaned=data_pile_summary[["PILE_ID","Quantity top","GCV top","BOTTOM GCV","AVERAGE AGING"]]
#-------------------------------------------------------
def process_coal_data(df, incoming_coal_gcv, ucl, lcl):
    threshold = 3700  # Given threshold value
    
    # Compute blended GCV values based on given conditions
    df['Blended GCV@20%'] = df.apply(lambda row: (0.8 * incoming_coal_gcv + 0.2 * row['GCV top']) 
                                     if row['Quantity top'] > 0.2 * threshold else 0, axis=1)
    
    df['Blended GCV @15%'] = df.apply(lambda row: (0.85 * incoming_coal_gcv + 0.15 * row['GCV top']) 
                                      if row['GCV top'] > 0.15 * threshold else 0, axis=1)
    
    df['Blended GCV @10%'] = df.apply(lambda row: (0.9 * incoming_coal_gcv + 0.1 * row['GCV top']) 
                                      if row['Blended GCV@20%'] > 0.1 * threshold else 0, axis=1)
    
    # Compute blending possibilities
    df['Blending possibility @ 20%'] = df['Blended GCV@20%'].apply(lambda x: x if lcl < x < ucl else 0)
    df['Blending possibility @ 15%'] = df['Blended GCV @15%'].apply(lambda x: x if lcl < x < ucl else 0)
    df['Blending possibility @ 10%'] = df['Blended GCV @10%'].apply(lambda x: x if lcl < x < ucl else 0)
    
    # Check blending possible
    df['Blending possible'] = df.apply(lambda row: 1 if (row['Blending possibility @ 20%'] + row['Blending possibility @ 15%'] + row['Blending possibility @ 10%']) > 0 else 0, axis=1)
    
    # Compute priority as per aging
    avg_aging = df['AVERAGE AGING'].mean()
    df['Priority as per aging'] = df.apply(lambda row: 1 if row['Blending possible'] == 1 and (row['AVERAGE AGING'] - avg_aging) > 0 else 0, axis=1)
    
    # Compute priority to create approach to bottom coal
    df['Priority to create approach to bottom coal'] = df.apply(lambda row: 1 if (row['BOTTOM GCV'] - row['GCV top']) > 100 else 0, axis=1)
    
    # Compute final priority
    df['PRIORITY'] = df.apply(lambda row: row['Blending possible'] + row['Priority as per aging'] + row['Priority to create approach to bottom coal'] if row['Blending possible'] == 1 else 0, axis=1)
    
    # Rank within each priority group based on AVERAGE AGING (higher aging gets higher rank)
    rank_within_priority = df.groupby('PRIORITY')['AVERAGE AGING'].rank(method='first', ascending=False)
    
    # Adjust PRIORITY based on ranking
    df['PRIORITY'] = df.apply(lambda row: 10 - int(rank_within_priority[row.name]) if row['PRIORITY'] > 0 else 0, axis=1)
    
    return round(df)

#Final_data=process_coal_data(pile_summary_cleaned,incoming_coal_gcv,ucl, lcl)

def coal_feeding_decision(df, incoming_coal_gcv, ucl, lcl):
    data_coal = get_data("SELECT * FROM cyms.pile_summary")
    total_coal = data_coal[['>3500', '3100-3500', '<3100']].sum().sum()
    data_coal['Percentage Above 3500'] = (data_coal['>3500'].sum() / total_coal) * 100
    data_coal['Percentage Below 3100'] = (data_coal['<3100'].sum() / total_coal) * 100
    
    decisions = {}
    
    decision_flags = {
        "Direct Feeding (Healthy Yard)": 0,
        "Direct Feeding (Good Quality, High Quantity)": 0,
        "Direct Feeding (Low Quality, No Good Coal)": 0,
        "Blending with Direct Feeding (In Range)": 0,
        "Blending with Direct Feeding (Out of Range)": 0,
        "Stacking": 0
    }
    
    if incoming_coal_gcv < ucl and incoming_coal_gcv > lcl and data_coal['Percentage Above 3500'].iloc[0] < 10:
        decisions["Direct Feeding (Healthy Yard)"] = 1
        decision_flags["Direct Feeding (Healthy Yard)"] = 1
    
    if incoming_coal_gcv > 3500 and incoming_coal_gcv < 4000 and data_coal['Percentage Below 3100'].iloc[0] > 70:
        decisions["Direct Feeding (Good Quality, High Quantity)"] = 1
        decision_flags["Direct Feeding (Good Quality, High Quantity)"] = 1
    
    if incoming_coal_gcv < 3000 and incoming_coal_gcv > 2300 and data_coal['Percentage Above 3500'].iloc[0] > 80:
        decisions["Direct Feeding (Low Quality, No Good Coal)"] = 1
        decision_flags["Direct Feeding (Low Quality, No Good Coal)"] = 1
    
    if incoming_coal_gcv > lcl and incoming_coal_gcv < ucl and data_coal['Percentage Above 3500'].iloc[0] > 10 and df[['Blending possibility @ 20%', 'Blending possibility @ 15%', 'Blending possibility @ 10%']].sum().sum() > 0:
        decisions["Blending with Direct Feeding (In Range) And PILE NO"] = df.loc[df['PRIORITY'].idxmax(), 'PILE_ID']
        decision_flags["Blending with Direct Feeding (In Range)"] = 1
    
    if (incoming_coal_gcv > ucl or incoming_coal_gcv < lcl) and df[['Blending possibility @ 20%', 'Blending possibility @ 15%', 'Blending possibility @ 10%']].sum().sum() > 0:
        decisions["Blending with Direct Feeding (Out of Range) And PILE NO"] = df.loc[df['PRIORITY'].idxmax(), 'PILE_ID']
        decision_flags["Blending with Direct Feeding (Out of Range)"] = 1
    
    if not decisions:
        decisions["Stacking"] = 1
        decision_flags["Stacking"] = 1
    
    decision_df = pd.DataFrame(list(decision_flags.items()), columns=["Decision Criteria", "Decision Flag"])
    
    return decisions, decision_df


layout = dbc.Container([
    dbc.Row([
        html.H3(
            "Direct Feed, Blending And Stacking Decision",
            style={"color": "white", "fontWeight": "bold", "textAlign": "center"}
        ),
    ]),
    dbc.Row([
        html.Div([
            html.H5("KINDLY PROVIDE THE INCOMING COAL INFORMATION BELOW - ", 
                    className="text-light mt-2", 
                    style={"padding-left": "15px"})
        ], style={"background-color": "#343a40", "padding": "10px", "border-radius": "5px", "margin-bottom": "10px"}),
    ]),
    dbc.Row([
    dbc.Col(html.Label("Incoming Coal GCV-")),
    dbc.Col(dcc.Input(id='incoming_coal_gcv', type='number', debounce=True), width=2),
    
    dbc.Col(html.Label("UCL -")),
    dbc.Col(dcc.Input(id='ucl', type='number', debounce=True), width=2),
    
    dbc.Col(html.Label("LCL -")),
    dbc.Col(dcc.Input(id='lcl', type='number', debounce=True), width=2),
    
    dbc.Col(dbc.Button("Process", id='process_button', color='success'), width=2)
], className='mb-4 text-center'),

    # Add loading spinner
    dbc.Row([
        dcc.Loading(
            id="loading-spinner",
            type="circle",  # You can use "default", "circle", or "dot"
            children=[
                dbc.Row([
                    dbc.Col(
                        dash_table.DataTable(
                            id='data-table',
                            style_table={'overflowX': 'auto'},
                            style_header={
                                'backgroundColor': 'black',  # Header background color
                                'color': 'white',  # Header text color
                                'fontWeight': 'bold',
                                'textAlign': 'center'
                            },
                            style_data={
                                'backgroundColor': 'black',  # Table background color
                                'color': 'white'  # Text color
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(30, 30, 30)'  # Dark gray for odd rows
                                },
                                {
                                    'if': {'column_id': 'Pile ID'},
                                    'backgroundColor': 'rgb(50, 50, 50)',  # Dark gray for specific column
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                }
                            ]
                        ), width=7
                    ),
                    dbc.Col([
                        dash_table.DataTable(
                            id='data-table-2',
                            #style_table={'overflowX': 'auto'},
                            style_header={
                                'backgroundColor': 'black',  # Header background color
                                'color': 'white',  # Header text color
                                'fontWeight': 'bold',
                                'textAlign': 'center'
                            },
                            style_data={
                                'backgroundColor': 'black',  # Table background color
                                'color': 'white'  # Text color
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(30, 30, 30)'  # Dark gray for odd rows
                                },
                                {
                                    'if': {'column_id': 'Pile ID'},
                                    'backgroundColor': 'rgb(50, 50, 50)',  # Dark gray for specific column
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{Decision Flag} > 0'  # Highlight rows where 'Decision Flag' > 0
                                    },
                                    'backgroundColor': 'green',
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                }
                            ]
                        ),
                        html.Br(),
                        dbc.Tabs([
                            dbc.Tab(label="Decision", tab_id="decision")
                        ], id="tabs", active_tab="decision"),
                        html.Div([
                            dbc.Button("- - -", id="decision_output", color="danger", style={"fontSize": "24px", "padding": "5px"})
                        ], className="d-grid gap-2")
                    ], width=4)
                ])
            ]
        )
    ]),
], fluid=True, style={'backgroundColor': '#323635', 'padding': '10px'})


@callback(
    [Output('data-table', 'data'), Output('data-table-2', 'data'),
     Output('data-table', 'columns'), Output('decision_output', 'children')],
    [Input('process_button', 'n_clicks')],
    [dash.dependencies.State('incoming_coal_gcv', 'value'),
     dash.dependencies.State('ucl', 'value'),
     dash.dependencies.State('lcl', 'value')]
)
def update_output(n_clicks, incoming_coal_gcv, ucl, lcl):
    if n_clicks is None or incoming_coal_gcv is None or ucl is None or lcl is None:
        return [], [], ""
    
    processed_df = process_coal_data(pile_summary_cleaned, incoming_coal_gcv, ucl, lcl)
    decision,decision_df = coal_feeding_decision(processed_df, incoming_coal_gcv, ucl, lcl)
    
    columns = [{"name": i, "id": i} for i in processed_df.columns]
    decision_text = html.Div([html.P(f"{k}: {v}") for k, v in decision.items()])
    
    return processed_df.to_dict('records'),decision_df.to_dict('records'), columns, decision_text
