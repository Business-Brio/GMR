from dash import html, dcc
import dash_bootstrap_components as dbc

layout = html.Div([
    html.H1("Welcome to the Input page!", className="text-center text-light"),
    
    # Heading above dropdown section with background color
    html.Div(
        html.H2("Coal Incoming Value", className="text-left text-light mt-6", style={"padding-left": "15px"}),
        style={"background-color": "#343a40", "padding": "10px", "border-radius": "5px"}
    ),
    # Three dropdown input fields
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id="dropdown_1",
            options=[
                {"label": "Coal Amount", "value": "coal_amount"},
                {"label": "GCV Value", "value": "gcv_value"},
                {"label": "Pile Name", "value": "pile_name"}
            ],
            placeholder="Select an option"
        ), width=4),
        
        dbc.Col(dbc.Input(id="text_input_1", placeholder="Enter value", type="text"), width=4),
        
        dbc.Col(dbc.Button("Submit", id="submit_button", color="primary", className="w-50"), width=4, className="d-flex justify-content-center"),
        html.Div(id="blank_div", style={"height": "20px"}),

    ], className="mt-3"),

    # Heading above dropdown section with background color
    html.Div(
        html.H2("Coal Reclaming Value", className="text-left text-light mt-6", style={"padding-left": "15px"}),
        style={"background-color": "#343a40", "padding": "10px", "border-radius": "5px"}
    ),

    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id="dropdown_1",
            options=[
                {"label": "Coal Amount", "value": "coal_amount"},
                {"label": "GCV Value", "value": "gcv_value"},
                {"label": "Pile Name", "value": "pile_name"}
            ],
            placeholder="Select an option"
        ), width=4),
        
        dbc.Col(dbc.Input(id="text_input_1", placeholder="Enter value", type="text"), width=4),
        
        dbc.Col(dbc.Button("Submit", id="submit_button", color="primary", className="w-50"), width=4, className="text-center"),
        html.Div(id="blank_div", style={"height": "20px"}),

    ], className="mt-3"),

    # Heading above dropdown section with background color
    html.Div(
        html.H2("Coal Incoming Value", className="text-left text-light mt-6", style={"padding-left": "15px"}),
        style={"background-color": "#343a40", "padding": "10px", "border-radius": "5px"}
    ),
    # Three dropdown input fields
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id="dropdown_1",
            options=[
                {"label": "Coal Amount", "value": "coal_amount"},
                {"label": "GCV Value", "value": "gcv_value"},
                {"label": "Pile Name", "value": "pile_name"}
            ],
            placeholder="Select an option"
        ), width=4),
        
        dbc.Col(dbc.Input(id="text_input_1", placeholder="Enter value", type="text"), width=4),
        
        dbc.Col(dbc.Button("Submit", id="submit_button", color="primary", className="w-50"), width=4, className="text-center"),
        html.Div(id="blank_div", style={"height": "20px"}),

    ], className="mt-3"),
])
