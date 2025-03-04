import plotly.graph_objects as go
import plotly.subplots as sp
import numpy as np
import dash
import pandas as pd
from dash import Dash, html, dcc,callback
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from sqlalchemy import create_engine

CONN_STRING = "postgresql+psycopg2://brioadmin:Gbsm%401234@briopgdb.postgres.database.azure.com:5432/gmr"

def get_data(query):
    # create a connection to the database
    engine = create_engine(CONN_STRING)
    data = pd.read_sql(query, engine)

    return data

layout = dbc.Container([
    dbc.Row([
        dbc.Col(dcc.Loading(  # Add loading spinner
                id="loading-bar",
                type="circle",  # or "default" / "dot"
                children=dcc.Graph(id="bar-chart2")
            ), width=11),  # Bar chart takes 8 columns
    ]),
    # Buttons for calculated metrics
    # dbc.Row([
    #     dbc.Col(dbc.Button("Max Aging: ", id="max-aging2", color="danger"), width=6),
    #     dbc.Col(dbc.Button("Avg Aging: ", id="avg-aging2", color="warning"), width=6),
    # ], className="mt-4"),
    # Interval component to update data every 60 seconds
    dcc.Interval(
        id="interval-update",
        interval=60*5000,  # 1 minute (in milliseconds)
        n_intervals=0  # Start at 0
    )
], fluid=True, style={'backgroundColor': '#323635', 'padding': '10px'})

@callback(
    Output("bar-chart2", "figure"),
     #Output("max-aging2", "children"), 
     #Output("avg-aging2", "children")],
    Input("interval-update", "n_intervals")
)

def update_charts(n_intervals):
    # Load data
    data = get_data("SELECT * FROM cyms.pile_summary")
    # Define required piles in the new order
    required_piles = ["1D", "2D", "3D", "4D", "1C", "2C", "3C", "4C", 
                        "1B", "2B", "3B", "4B", "1A", "2A", "3A", "4A"]

    # Compute average GCV and sum of AVAILABLE QUANTITY for Top and Bottom per Pile_id
    grouped_data=data[["PILE_ID","MAX AGING","AVERAGE AGING"]]
    grouped_data = grouped_data.reset_index()

    # Ensure only the required piles are present in the new order
    grouped_data = grouped_data.set_index("PILE_ID").reindex(required_piles, fill_value=0).reset_index()

    # Total and average calculations
    max_aging = grouped_data["MAX AGING"].max()
    min_aging = grouped_data["AVERAGE AGING"].mean()
    avg_aging=round(min_aging)

    # Create subplot figure (4x4 grid)
    bar_fig = make_subplots(rows=4, cols=4, subplot_titles=required_piles)

    # Add bar plots to each subplot
    row, col = 1, 1
    for i, row_data in grouped_data.iterrows():
        # Round the GCV values to integers
        MAX_AGING_rounded = round(row_data["MAX AGING"])
        AVERAGE_AGING_rounded = round(row_data["AVERAGE AGING"])

        bar_fig.add_trace(
            go.Bar(
                x=["MAX AGING", "AVG AGING"],
                y=[ MAX_AGING_rounded, AVERAGE_AGING_rounded ],
                name=row_data["PILE_ID"],
                marker=dict(color=["#055e6e","#08bdd1"]),
                text=[MAX_AGING_rounded, AVERAGE_AGING_rounded],  # Display values
                textposition='auto',
            ),
            row=row,
            col=col,
        )
        col += 1
        if col > 4:
            col = 1
            row += 1

    # Update layout with white text and updated background colors
    bar_fig.update_layout(
        title_text="<b><u> GCV and Available Quantity of Piles </u></b>",
        title_font=dict(color="white"),
        title_x=0.5,
        height=550,
        width=1450,
        showlegend=False,
        plot_bgcolor="#323635",  # Set plot background color to #323635
        paper_bgcolor="#323635",  # Set paper background color to #323635
        font=dict(color="white"),  # Set all text to white
        xaxis_title="",
        yaxis_title="",
        yaxis=dict(
            showticklabels=False,  # Hide y-axis labels
            showgrid=False,  # Hide y-axis grid lines
            #zeroline=False,  # Hide y-axis zero line
        ),
    )
    # Hide axis labels and grid lines for each subplot
    for i in range(1, 5):  # 4 rows
        for j in range(1, 5):  # 4 columns
            bar_fig.update_yaxes(
                showticklabels=False,  # Hide y-axis labels
                showgrid=False,  # Hide y-axis grid lines
                #zeroline=False,  # Hide y-axis zero line
                row=i,
                col=j
            )

    return (bar_fig)
           # f"Max Aging: {max_aging}", f"Avg Aging: {avg_aging}")



