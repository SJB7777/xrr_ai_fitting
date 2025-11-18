# xrr_app.py
import dash
from dash import html, dcc, Input, Output, State, callback, dash_table
import plotly.graph_objects as go
import numpy as np
from app.components.film_3d import generate_film_stack_image

dash.register_page(__name__, path="/xrr_app")

# --- Constants ---
MATERIALS = ["Si", "SiO2", "Al2O3", "Cr", "Au", "Ti", "Ta2O5"]

# Initial sample data
INITIAL_LAYERS = [
    {"layer": "Si Substrate", "thickness": "∞", "density": "2.33", "roughness": "0.2"},
    {"layer": "SiO₂", "thickness": "10.0", "density": "2.20", "roughness": "0.3"},
    {"layer": "Cr", "thickness": "5.0", "density": "7.19", "roughness": "0.5"},
]

# Material database
MATERIAL_DB = [
    {"formula": "Si", "name": "Silicon", "density": "2.33"},
    {"formula": "SiO₂", "name": "Silicon Dioxide", "density": "2.20"},
    {"formula": "Al₂O₃", "name": "Aluminum Oxide", "density": "3.95"},
    {"formula": "Cr", "name": "Chromium", "density": "7.19"},
    {"formula": "Au", "name": "Gold", "density": "19.32"},
    {"formula": "Ti", "name": "Titanium", "density": "4.51"},
    {"formula": "Ta₂O₅", "name": "Tantalum Pentoxide", "density": "8.20"},
]

# --- Layout ---
layout = html.Div([
    html.Div([
        # === Left Panel: Main Workflow ===
        html.Div([
            # Workflow Navigation
            html.Div([
                html.Div([
                    html.Div("1", className="workflow-step-number"),
                    html.Div([
                        html.Div("Data Input", className="workflow-step-title"),
                        html.Div("Load experimental XRR data", className="workflow-step-desc")
                    ])
                ], className="workflow-step active", id="step-1"),
                
                html.Div([], className="workflow-arrow"),
                
                html.Div([
                    html.Div("2", className="workflow-step-number"),
                    html.Div([
                        html.Div("AI Initialization", className="workflow-step-title"),
                        html.Div("Deep learning prediction", className="workflow-step-desc")
                    ])
                ], className="workflow-step", id="step-2"),
                
                html.Div([], className="workflow-arrow"),
                
                html.Div([
                    html.Div("3", className="workflow-step-number"),
                    html.Div([
                        html.Div("Refinement", className="workflow-step-title"),
                        html.Div("Iterative parameter fitting", className="workflow-step-desc")
                    ])
                ], className="workflow-step", id="step-3"),
            ], className="workflow-nav"),

            # Section 1: Data Input
            html.Div([
                html.Div([
                    html.Div("INPUT: EXPERIMENTAL DATA", className="section-title"),
                    html.Div([
                        html.Button("📋 Template", id="btn-template", className="action-btn"),
                        html.Button("🗑️ Clear", id="btn-clear", className="action-btn"),
                    ], className="section-actions")
                ], className="section-header"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div("📁 Drop XRR data file here", className="upload-text"),
                            html.P("Supported: *.txt, *.xy, *.dat (2-column: q, I)", 
                                   className="upload-hint")
                        ], className="upload-zone", id="data-upload"),
                        dcc.Upload(id="upload-data", children=html.Div(), 
                                  style={"display": "none"})
                    ]),
                    html.Div([
                        html.Div([], className="status-dot status-ready"),
                        html.Span("Awaiting data...", id="upload-status")
                    ], className="status-bar")
                ], className="section-content")
            ], className="section"),

            # Section 2: Model Definition
            html.Div([
                html.Div([
                    html.Div("MODEL DEFINITION", className="section-title"),
                    html.Div([
                        html.Button("💾 Save", id="btn-save-model", className="action-btn"),
                        html.Button("📂 Load", id="btn-load-model", className="action-btn"),
                    ], className="section-actions")
                ], className="section-header"),
                html.Div([
                    # Parameter inputs
                    html.Div([
                        html.Div([
                            html.Label("Formula", className="input-label"),
                            dcc.Input(id="material-input", type="text", 
                                     placeholder="e.g., SiO2", className="param-input")
                        ], className="input-group"),
                        html.Div([
                            html.Label("Thickness (nm)", className="input-label"),
                            dcc.Input(id="thickness-input", type="number", 
                                     placeholder="10.0", className="param-input")
                        ], className="input-group"),
                        html.Div([
                            html.Label("Density (g/cm³)", className="input-label"),
                            dcc.Input(id="density-input", type="number", 
                                     placeholder="2.20", className="param-input")
                        ], className="input-group"),
                        html.Div([
                            html.Label("Roughness (nm)", className="input-label"),
                            dcc.Input(id="roughness-input", type="number", 
                                     placeholder="0.3", className="param-input")
                        ], className="input-group"),
                    ], className="input-row"),
                    
                    html.Button("➕ Add Layer", id="btn-add-layer", className="btn-primary"),
                    
                    # Layers table
                    dash_table.DataTable(
                        id='layers-table',
                        columns=[
                            {'name': 'Layer', 'id': 'layer', 'editable': False},
                            {'name': 'Thickness (nm)', 'id': 'thickness', 'type': 'numeric'},
                            {'name': 'Density (g/cm³)', 'id': 'density', 'type': 'numeric'},
                            {'name': 'Roughness (nm)', 'id': 'roughness', 'type': 'numeric'},
                        ],
                        data=INITIAL_LAYERS,
                        style_table={'marginTop': '15px'},
                        style_header={
                            'backgroundColor': '#e2e8f0',
                            'color': '#1e293b',
                            'fontWeight': '600',
                            'border': '1px solid #cbd5e1'
                        },
                        style_cell={
                            'backgroundColor': 'white',
                            'color': '#1e293b',
                            'border': '1px solid #e2e8f0',
                            'padding': '10px'
                        },
                        style_data_conditional=[
                            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8fafc'}
                        ],
                        row_deletable=True,
                    )
                ], className="section-content")
            ], className="section"),

            # Section 3: Visualization (Graph + 3D)
            html.Div([
                html.Div([
                    html.Div("MODEL VISUALIZATION", className="section-title"),
                    html.Div([
                        html.Button("🔄 Refresh", id="btn-refresh-viz", className="action-btn"),
                    ], className="section-actions")
                ], className="section-header"),
                html.Div([
                    html.Div([
                        # Reflectivity Graph
                        html.Div([
                            dcc.Graph(id="reflectivity-graph", 
                                     figure=go.Figure(layout={
                                         'plot_bgcolor': '#f8fafc',
                                         'paper_bgcolor': 'white',
                                         'margin': {'l': 60, 'r': 30, 't': 30, 'b': 60}
                                     }), 
                                     className="main-graph")
                        ], className="graph-container"),
                        
                        # 3D Film Viewer
                        html.Div([
                            html.Div([
                                html.Div("3D STRUCTURE VIEW", className="film-3d-title"),
                                html.Div([
                                    html.Button("TOP", id="btn-view-top", className="control-btn"),
                                    html.Button("SIDE", id="btn-view-side", className="control-btn"),
                                    html.Button("ISO", id="btn-view-iso", className="control-btn"),
                                ], className="film-3d-controls")
                            ], className="film-3d-header"),
                            html.Div([
                                html.Img(id="film-3d-image", 
                                        src=generate_film_stack_image(INITIAL_LAYERS, "iso"),
                                        style={"width": "100%", "height": "100%", "objectFit": "contain"})
                            ], className="film-3d-viewport")
                        ], className="film-3d-container")
                    ], className="visualization-container")
                ], className="section-content")
            ], className="section"),

            # Section 4: Fitting Engine
            html.Div([
                html.Div([
                    html.Div("FITTING ENGINE", className="section-title"),
                    html.Div([
                        html.Button("⚙️ Settings", id="btn-fit-settings", className="action-btn"),
                    ], className="section-actions")
                ], className="section-header"),
                html.Div([
                    html.Div([
                        html.Button("🤖 Initialize AI", id="btn-init-ai", 
                                   className="fit-btn btn-secondary"),
                        html.Button("▶️ Start Fitting", id="btn-start-fit", 
                                   className="fit-btn btn-primary"),
                    ], className="fitting-controls"),
                    
                    html.Div([
                        html.Div([
                            html.Div(className="progress-fill", 
                                    style={"width": "34%", "background": "#3b82f6"})
                        ], className="progress-bar"),
                        html.Div([
                            html.Span("Iteration: 340/1000", className="progress-text"),
                            html.Span("χ²: 0.087", className="progress-value")
                        ], className="progress-info")
                    ], className="progress-container"),
                    
                    html.Div([
                        html.H4("Execution Log", className="log-title"),
                        html.Div([
                            html.Div("14:35:23 | AI model loaded: xrr_cnn_v3.h5", className="log-entry"),
                            html.Div("14:35:24 | Initial guess: χ² = 0.847", className="log-entry"),
                            html.Div("14:35:25 | Refinement started...", className="log-entry"),
                        ], className="log-box", id="fit-log")
                    ], className="log-container")
                ], className="section-content")
            ], className="section"),

        ], className="left-panel"),

        # === Right Panel: Materials & Results ===
        html.Div([
            # Material Library
            html.Div([
                html.Div([
                    html.Div("MATERIAL LIBRARY", className="section-title"),
                ], className="section-header"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div(mat["formula"], className="material-formula"),
                            html.Div(f"{mat['density']} g/cm³", className="material-density"),
                        ], className="material-item", id=f"mat-{mat['formula'].replace('₂','2').replace('₅','5')}") 
                        for mat in MATERIAL_DB
                    ], className="material-library")
                ], className="section-content")
            ], className="section"),

            # Fit Status
            html.Div([
                html.Div([
                    html.Div("FIT STATUS", className="section-title"),
                ], className="section-header"),
                html.Div([
                    html.Div([
                        html.Div("Status", className="result-label"),
                        html.Div("CONVERGED", className="result-value", 
                                style={"color": "#10b981", "fontWeight": "700"})
                    ], className="result-card"),
                    html.Div([
                        html.Div("R-factor", className="result-label"),
                        html.Div("0.0087", className="result-value")
                    ], className="result-card"),
                    html.Div([
                        html.Div("Total Thickness", className="result-label"),
                        html.Div("18.01 nm", className="result-value")
                    ], className="result-card"),
                    html.Div([
                        html.Div("Layers", className="result-label"),
                        html.Div("4", className="result-value")
                    ], className="result-card"),
                ], className="result-grid")
            ], className="section"),

            # Final Parameters
            html.Div([
                html.Div([
                    html.Div("FINAL PARAMETERS", className="section-title"),
                ], className="section-header"),
                html.Div([
                    dash_table.DataTable(
                        id='final-params-table',
                        columns=[
                            {'name': 'Layer', 'id': 'layer'},
                            {'name': 'Value', 'id': 'final'},
                        ],
                        data=[
                            {"layer": "SiO₂", "final": "10.23±0.15"},
                            {"layer": "Cr", "final": "4.87±0.08"},
                            {"layer": "Al₂O₃", "final": "2.91±0.12"},
                        ],
                        style_table={'backgroundColor': 'transparent'},
                        style_cell={
                            'backgroundColor': 'white',
                            'color': '#1e293b',
                            'padding': '8px',
                            'border': '1px solid #e2e8f0',
                            'fontSize': '0.8rem'
                        }
                    )
                ], className="section-content")
            ], className="section"),

            # Export
            html.Div([
                html.Button("💾 Export Results", id="btn-export", 
                           className="btn-primary", style={"width": "100%"})
            ], className="section", style={"padding": "0", "border": "none"}),

        ], className="right-panel")

    ], className="main-container")
])

# === Callbacks ===

# Update layers table from multiple sources
@callback(
    Output("layers-table", "data", allow_duplicate=True),
    [Input(f"mat-{mat.replace('₂','2').replace('₅','5')}", "n_clicks") for mat in [m["formula"] for m in MATERIAL_DB]] +
    [Input("btn-add-layer", "n_clicks"),
     Input("btn-init-ai", "n_clicks")],
    State("layers-table", "data"),
    State("material-input", "value"),
    State("thickness-input", "value"),
    State("density-input", "value"),
    State("roughness-input", "value"),
    prevent_initial_call=True
)
def update_layers_table(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Extract states (last 4 arguments)
    layers_data = args[-4]
    material_input = args[-3]
    thickness_input = args[-2]
    density_input = args[-1]
    roughness_input = args[-2] if len(args) > 5 else None  # Fix index
    
    # Material mapping
    material_map = {
        "mat-Si": {"layer": "Si", "thickness": "100", "density": "2.33", "roughness": "0.2"},
        "mat-SiO2": {"layer": "SiO₂", "thickness": "10", "density": "2.20", "roughness": "0.3"},
        "mat-Al2O3": {"layer": "Al₂O₃", "thickness": "5", "density": "3.95", "roughness": "0.4"},
        "mat-Cr": {"layer": "Cr", "thickness": "5", "density": "7.19", "roughness": "0.5"},
        "mat-Au": {"layer": "Au", "thickness": "10", "density": "19.32", "roughness": "0.5"},
        "mat-Ti": {"layer": "Ti", "thickness": "10", "density": "4.51", "roughness": "0.3"},
        "mat-Ta2O5": {"layer": "Ta₂O₅", "thickness": "10", "density": "8.20", "roughness": "0.4"},
    }
    
    # Create new layer
    new_layer = None
    if button_id.startswith("mat-"):
        new_layer = material_map.get(button_id)
    elif button_id == "btn-add-layer" and material_input:
        new_layer = {
            "layer": material_input,
            "thickness": str(thickness_input or "10.0"),
            "density": str(density_input or "2.0"),
            "roughness": str(roughness_input or "0.3")
        }
    
    # Add layer
    if new_layer:
        layers_data = layers_data.copy()
        # Insert before substrate (last row)
        layers_data.insert(len(layers_data)-1, new_layer)
        return layers_data
    
    # AI initialization
    if button_id == "btn-init-ai":
        import random
        return [
            {"layer": "Si Substrate", "thickness": "∞", "density": "2.33", "roughness": "0.2"},
            {"layer": "SiO₂", "thickness": f"{random.uniform(8, 12):.1f}", 
             "density": "2.20", "roughness": f"{random.uniform(0.2, 0.4):.1f}"},
            {"layer": "Cr", "thickness": f"{random.uniform(4, 6):.1f}", 
             "density": "7.19", "roughness": f"{random.uniform(0.4, 0.6):.1f}"},
        ]
    
    return layers_data

# Update 3D view
@callback(
    Output("film-3d-image", "src"),
    Input("layers-table", "data"),
    Input("btn-view-top", "n_clicks"),
    Input("btn-view-side", "n_clicks"),
    Input("btn-view-iso", "n_clicks"),
    prevent_initial_call=False
)
def update_3d_view(layers_data, top_clicks, side_clicks, iso_clicks):
    ctx = dash.callback_context
    view = "iso"
    if ctx.triggered:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "btn-view-top":
            view = "top"
        elif button_id == "btn-view-side":
            view = "side"
    
    return generate_film_stack_image(layers_data or INITIAL_LAYERS, view)

# Update reflectivity graph
@callback(
    Output("reflectivity-graph", "figure"),
    Input("layers-table", "data"),
    prevent_initial_call=False
)
def update_graph(layers_data):
    # Generate mock XRR data
    q = np.logspace(-2, 1, 500)
    intensity = q**(-4) * np.exp(-0.1 * q)  # Simple decay
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=q, y=intensity,
        mode='lines',
        name='Experimental',
        line=dict(color='#3b82f6', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=q, y=intensity * 0.95,
        mode='lines',
        name='Simulated',
        line=dict(color='#10b981', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="XRR Reflectivity Curve",
        xaxis_title="q (Å⁻¹)",
        yaxis_title="Intensity (a.u.)",
        yaxis_type="log",
        plot_bgcolor='#f8fafc',
        paper_bgcolor='white',
        font=dict(color='#1e293b'),
        margin=dict(l=60, r=30, t=60, b=60),
        legend=dict(x=0.02, y=0.98)
    )
    
    return fig