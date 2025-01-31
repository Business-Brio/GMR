from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Initialize the Dash app with a dark theme
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
app.title = "Multi-Page Dash App"

# Define the navigation bar
navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("GMR Kamalanga Energy Ltd.", className="ms-2"),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Input", href="/cyms", active="exact")),
            dbc.NavItem(dbc.NavLink("GCV", href="/gcv", active="exact")),
            dbc.NavItem(dbc.NavLink("BLEND", href="/blend", active="exact")),
            dbc.NavItem(dbc.NavLink("STACK", href="/stack", active="exact")),
            dbc.NavItem(dbc.NavLink("AGING", href="/aging", active="exact")),
        ], className="ms-auto", navbar=True)
    ]),
    color="primary",
    dark=True
)

# Define the layout for each page
def create_page_layout(page_name):
    return html.Div([
        html.H1(page_name, className="text-center text-light mt-5"),
        html.P(f"Welcome to the {page_name} page!", className="text-center text-light")
    ])

# Define the app layout
app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    html.Div(id="page-content", className="mt-4")
])

# Update page content based on URL
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/gcv":
        return create_page_layout("GCV")
    elif pathname == "/blend":
        return create_page_layout("BLEND")
    elif pathname == "/stack":
        return create_page_layout("STACK")
    elif pathname == "/aging":
        return create_page_layout("AGING")
    # Default page
    return create_page_layout("Input")

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
