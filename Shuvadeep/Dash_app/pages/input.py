import dash
from dash import dcc, html, Input, Output,callback
import dash_bootstrap_components as dbc

# Define table headings
STACKING_HEADINGS = ["STACKING DATE", "Time", "RAKE NO", "SPUR", "SUB PILE", "TOP/BOTTOM", "ST QNTY", "GCV"]
RECLAIMING_HEADINGS = ["RECLAIMING DATE", "Time", "PILE", "TOP/BOTTOM", "RC QNTY", "GCV"]
INCOMING_HEADINGS = ["INCOMING DATE", "Time", "SPUR", "ST QNTY", "GCV"]


# Define app layout
table_div = html.Div(id='output-div')

layout = dbc.Container([
    dbc.Row([
        dbc.Col(dbc.Button("Stacking", id='stacking-btn', color='primary', className='w-100'), width=4),
        dbc.Col(dbc.Button("Reclaiming", id='reclaiming-btn', color='secondary', className='w-100'), width=4),
        dbc.Col(dbc.Button("Incoming", id='incoming-btn', color='success', className='w-100'), width=4),
    ], className='mb-4 text-center'),
    table_div
])


# Define callback function
@callback(
    Output('output-div', 'children'),
    [Input('stacking-btn', 'n_clicks'),
     Input('reclaiming-btn', 'n_clicks'),
     Input('incoming-btn', 'n_clicks')]
)
def update_output(stacking_clicks, reclaiming_clicks, incoming_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        headings = STACKING_HEADINGS  # Default selection
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'stacking-btn':
            headings = STACKING_HEADINGS
        elif button_id == 'reclaiming-btn':
            headings = RECLAIMING_HEADINGS
        elif button_id == 'incoming-btn':
            headings = INCOMING_HEADINGS
        else:
            return html.Div()
    
    return html.Div([
        html.Div([
            html.H5("KINDLY PROVIDE THE FOLLOWING INFORMATION BELOW - ", className="text-light mt-2", style={"padding-left": "15px"})
        ], style={"background-color": "#343a40", "padding": "10px", "border-radius": "5px", "margin-bottom": "10px"}),
        dbc.Row([
            dbc.Col(dbc.Input(id=f"input_{i}", placeholder=f"Enter {h}", type="text"), width=3)
            for i, h in enumerate(headings)
        ], className="mt-2"),
        html.Div(id="blank_div", style={"height": "20px"}),
        dbc.Row([
            dbc.Col( width=4, className="text-center"),
            dbc.Col(dbc.Button("Submit", id="submit_button", color="primary", className="w-50"), width=4, className="text-center")])
    ])
