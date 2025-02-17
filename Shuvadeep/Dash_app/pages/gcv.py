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
                children=dcc.Graph(id="bar-chart")
            ), width=8),  # Bar chart takes 8 columns
        dbc.Col(dcc.Loading(  # Add loading spinner
                id="loading-pie",
                type="circle",
                children=dcc.Graph(id="pie-chart")
            ), width=4)   # Pie chart takes 4 columns
    ]),
    # Buttons for calculated metrics
    dbc.Row([
        dbc.Col(dbc.Button("Total Top Qty: ", id="total-top-qty", color="warning"), width=2),
        dbc.Col(dbc.Button("Total Btm Qty: ", id="total-btm-qty", color="warning"), width=2),
        dbc.Col(dbc.Button("Avg Top GCV: ", id="avg-top-gcv", color="success"), width=2),
        dbc.Col(dbc.Button("Avg Btm GCV: ", id="avg-btm-gcv", color="success"), width=2),
        dbc.Col(dbc.Button("Max Aging: ", id="max-aging", color="danger"), width=2),
        dbc.Col(dbc.Button("Avg Aging: ", id="avg-aging", color="danger"), width=2),
    ], className="mt-4"),
    # Interval component to update data every 60 seconds
    dcc.Interval(
        id="interval-update",
        interval=60*5000,  # 1 minute (in milliseconds)
        n_intervals=0  # Start at 0
    )
], fluid=True, style={'backgroundColor': '#323635', 'padding': '10px'})

@callback(
    [Output("bar-chart", "figure"), Output("pie-chart", "figure"),
     Output("total-top-qty", "children"), Output("total-btm-qty", "children"),
     Output("avg-top-gcv", "children"), Output("avg-btm-gcv", "children"),
     Output("max-aging", "children"), Output("avg-aging", "children")],
    Input("interval-update", "n_intervals")
)

def update_charts(n_intervals):
    # Load data
    data = get_data("SELECT * FROM cyms.pile_details")
    #data = 
    # Define required piles in the new order
    required_piles = ["1D", "2D", "3D", "4D", "1C", "2C", "3C", "4C", 
                      "1B", "2B", "3B", "4B", "1A", "2A", "3A", "4A"]

    # Compute average GCV and sum of AVAILABLE QUANTITY for Top and Bottom per Pile_id
    grouped_data = data.groupby(["pile_id", "TOP/BOTTOM"]).agg({
        'gcv': 'mean',
        'AVAILABLE QUANTITY': 'sum',
        'aging': ['max', 'mean']  # Assuming ST QNTY represents AVAILABLE QUANTITY
    }).unstack(fill_value=0)
    # Drop columns where all values are NaN
    cleaned_data = grouped_data.dropna(axis=1, how='all')

    # Convert MultiIndex columns to a single level by joining names
    cleaned_data.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in cleaned_data.columns]

    # Drop any column that has 'nan' in its name (if misnamed)
    grouped_data = cleaned_data.loc[:, ~cleaned_data.columns.str.contains('nan', case=False, na=False)]

    grouped_data.columns = ['BTM GCV', 'TOP GCV', 'BTM QTY', 'TOP QTY','BTM MAX AGING', 'TOP MAX AGING', 'BTM MEAN AGING','TOP MEAN AGING']
    grouped_data = grouped_data.reset_index()

    # Ensure only the required piles are present in the new order
    grouped_data = grouped_data.set_index("pile_id").reindex(required_piles, fill_value=0).reset_index()

    # Total and average calculations
    total_top_qty = grouped_data["TOP QTY"].sum()
    total_btm_qty = grouped_data["BTM QTY"].sum()
    avg_top_gcv = round(grouped_data["TOP GCV"].mean(), 2)
    avg_btm_gcv = round(grouped_data["BTM GCV"].mean(), 2)
    max_aging = max(grouped_data["BTM MAX AGING"].max(), grouped_data["TOP MAX AGING"].max())
    min_aging = min(grouped_data["BTM MEAN AGING"].mean(), grouped_data["TOP MEAN AGING"].mean())
    avg_aging=round(min_aging)

    # Create subplot figure (4x4 grid)
    bar_fig = make_subplots(rows=4, cols=4, subplot_titles=required_piles)

    # Add bar plots to each subplot
    row, col = 1, 1
    for i, row_data in grouped_data.iterrows():
        # Round the GCV values to integers
        top_gcv_rounded = round(row_data["TOP GCV"])
        btm_gcv_rounded = round(row_data["BTM GCV"])
        top_qty = row_data["TOP QTY"]
        btm_qty = row_data["BTM QTY"]


        bar_fig.add_trace(
            go.Bar(
                x=["T QTY", "T GCV", "B QTY","B GCV"],
                y=[top_qty, top_gcv_rounded, btm_qty, btm_gcv_rounded ],
                name=row_data["pile_id"],
                marker=dict(color=["#cc6225", "#2a9c52", "#cc6225", "#2a9c52"])
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
        height=500,
        width=950,
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

    # Categorize GCV values
    def categorize_gcv(value):
        if value > 3500:
            return "Above 3500"
        elif 3100 <= value <= 3500:
            return "3100 - 3500"
        else:
            return "Below 3100"

    grouped_data['TOP GCV Category'] = grouped_data['TOP GCV'].apply(categorize_gcv)
    grouped_data['BTM GCV Category'] = grouped_data['BTM GCV'].apply(categorize_gcv)

    # Count occurrences in each category
    top_gcv_counts = grouped_data['TOP GCV Category'].value_counts()
    btm_gcv_counts = grouped_data['BTM GCV Category'].value_counts()

    # Define custom colors
    custom_colors = {
        "Above 3500": "#038080",  # Teal
        "3100 - 3500": "#04c988",  # Green
        "Below 3100": "#94a2f7"  # Blue
    }


    # Create pie charts
    pie_fig = make_subplots(rows=2, cols=1, subplot_titles=["Top GCV Distribution", "Bottom GCV Distribution"], specs=[[{"type": "domain"}], [{"type": "domain"}]])

    pie_fig.add_trace(
        go.Pie(labels=top_gcv_counts.index, values=top_gcv_counts.values, name="Top GCV",
        marker=dict(colors=[custom_colors[label] for label in btm_gcv_counts.index])),
        row=1, col=1,
    )

    pie_fig.add_trace(
        go.Pie(labels=btm_gcv_counts.index, values=btm_gcv_counts.values, name="Bottom GCV",
        marker=dict(colors=[custom_colors[label] for label in btm_gcv_counts.index])),
        row=2, col=1
    )

    # Update layout
    pie_fig.update_layout(
        title_text="<b><u> GCV Value Distribution Across Piles </u></b>",
        title_x=0.5,
        title_font=dict(color="white"),
        height=500,
        width=400,
        showlegend=True,
        legend=dict(  # Centered horizontally
        y=0.6,  # Positioned between the pies
        xanchor="center",
        yanchor="middle",
        bgcolor="#323635",  # Match background
        font=dict(color="white")
        ),
        plot_bgcolor="#323635",
        paper_bgcolor="#323635",
        font=dict(color="white")
    )
    return (bar_fig, pie_fig, 
            f"Total Top Qty: {total_top_qty}", f"Total Btm Qty: {total_btm_qty}",
            f"Avg Top GCV: {avg_top_gcv}", f"Avg Btm GCV: {avg_btm_gcv}",
            f"Max Aging: {max_aging}", f"Avg Aging: {avg_aging}")



