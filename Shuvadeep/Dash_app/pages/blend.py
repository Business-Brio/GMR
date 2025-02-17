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

data = get_data("SELECT * FROM cyms.blending")
data= data.iloc[:, 1:12]
data_rounded = data.applymap(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)

layout = dbc.Container([
    dbc.Row([
        html.H3(
    "Direct Feed, Blending And Stacking Decision",
    style={"color": "white", "fontWeight": "bold", "textAlign": "center"}
),]),
    dbc.Row([
        dbc.Col(dbc.Button("Direct Feeding", id='stacking-btn', color='danger', className='w-100'), width=4),
        dbc.Col(dbc.Button("ReclDirect Feeding With Blendingaiming", id='reclaiming-btn', color='danger', className='w-100'), width=4),
        dbc.Col(dbc.Button("Stalking", id='incoming-btn', color='success', className='w-100'), width=4),
    ], className='mb-4 text-center'),
    dbc.Row([    
        dbc.Col(
        dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in data.columns],
        data=data_rounded.to_dict('records'),
        style_table={'width': '50%'},
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
    ), width=8),
    #     dbc.Col(
    #     dbc.Row([
    #       dbc.Col(  
    #     dcc.Dropdown(
    #         id='pile-dropdown',
    #         options=[{'label': pile, 'value': pile} for pile in data['pile_id']],
    #         value='PILE 1A'
    #     ),),
    #       dbc.Col(dcc.Graph(id='pie-chart2')),])
    # ,width=4)
    ]),


], fluid=True, style={'backgroundColor': '#323635', 'padding': '10px'})

@callback(
    Output('pie-chart2', 'figure'),
    Input('pile-dropdown', 'value')
)
def update_pie(selected_pile):
    filtered_df = data[data['pile_id'] == selected_pile]
    fig = px.pie(names=["Blending GCV @20%", "Blending GCV @15%"],
                 values=[filtered_df.iloc[:,6]['Blending GCV @20%'], filtered_df.iloc[:,7]['Blending GCV @15%']],
                 title=f'Blending GCV for {selected_pile}')
    return fig

