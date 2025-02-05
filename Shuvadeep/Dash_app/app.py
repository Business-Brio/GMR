from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from pages import input, gcv, blend, stack, aging

# Initialize the Dash app with a dark theme
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
app.title = "CYMS App"

# Define the navigation bar
navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand([
    html.Img(src="/assets/logo.jpg", height="40px", className="me-2"),  # Replace with your logo path
    "CYMS | GMR Kamalanga Energy Ltd."
    ], className="ms-2"),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Input", href="/input", active="exact")),
            dbc.NavItem(dbc.NavLink("GCV", href="/gcv", active="exact")),
            dbc.NavItem(dbc.NavLink("BLEND", href="/blend", active="exact")),
            dbc.NavItem(dbc.NavLink("STACK", href="/stack", active="exact")),
            dbc.NavItem(dbc.NavLink("AGING", href="/aging", active="exact")),
        ], className="ms-auto", navbar=True)
    ]),
    color="primary",
    dark=True
)

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
        return gcv.layout
    elif pathname == "/blend":
        return blend.layout
    elif pathname == "/stack":
        return stack.layout
    elif pathname == "/aging":
        return aging.layout
    # Default page
    return input.layout

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)