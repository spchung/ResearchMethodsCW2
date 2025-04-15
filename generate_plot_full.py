import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Load the data
df = pd.read_csv('full_set/summary_full_set.csv')

# reorder
new_order = [
    'mc_run_id', 'diet_group','mean_ghgs', 'mean_ghgs_ch4', 
    'mean_ghgs_n2o', 'mean_land', 'mean_watuse', 
    'mean_watscar', 'mean_eut','mean_bio','mean_acid',
    'sd_ghgs','sd_land','sd_watscar',
    'sd_eut','sd_ghgs_ch4','sd_ghgs_n2o','sd_bio','sd_watuse',
    'sd_acid','n_participants',
]

df = df[new_order]

# Define the metrics we want to visualize (excluding the 'sd_' columns for the main plot)
metrics = [col for col in df.columns if col.startswith('mean_')]

# First part: select 10 random mc_run_ids
mc_run_ids = df['mc_run_id'].unique()
# np.random.seed(21)  # For reproducibility
selected_mc_run_ids = np.random.choice(mc_run_ids, size=10, replace=False)

# Second part: filter the DataFrame to keep only rows with the selected mc_run_ids
filtered_df = df[df['mc_run_id'].isin(selected_mc_run_ids)]
filtered_df = filtered_df.drop(columns=['mc_run_id'])  # Drop mc_run_id for plotting

# Define a color palette for the diet groups
# colors = {
#     'vegan': '#1b9e77',      # Green
#     'veggie': '#7570b3',     # Purple
#     'fish': '#66a61e',       # Olive
#     'meat50': '#e6ab02',     # Gold
#     'meat': '#d95f02',       # Orange
#     'meat100': '#e7298a'     # Pink
# }

colors = {
    'veggie': '#3CB371',     # Medium sea green
    'vegan': '#98FB98',      # Pale green
    'fish': '#4682B4',       # Steel blue
    'meat': '#FF8C00',       # Dark orange
    'meat50': '#FF4500',     # Orange red
    'meat100': '#FF0000'     # Bright red
}

# Create a color column for the plot
filtered_df['color'] = filtered_df['diet_group'].map(colors)

# Create more readable labels for the metrics
label_map = {
    'mean_ghgs': 'GHG Emissions (kg)',
    'mean_ghgs_ch4': 'Methane (kg)',
    'mean_ghgs_n2o': 'Nitrous Oxide (kg)',
    'mean_land': 'Land Use (m²)',
    'mean_watuse': 'Water Use (m³)',
    'mean_eut': 'Eutrophication (g PO₄e)',
    'mean_watscar': 'Water Scarcity',
    'mean_acid': 'Acidification',
    'mean_bio': 'Biodiversity Impact',
}

dimensions = []

for metric in metrics:
    sd_metric = metric.replace('mean_', 'sd_')
    
    mean_values = filtered_df[metric]
    sd_values = filtered_df[sd_metric]

    # print(f"Processing {metric}: mean range = {mean_values.min()} to {mean_values.max()}, sd range = {sd_values.min()} to {sd_values.max()}")
    
    # use one sd from max and min for max and min value on each y axis
    min_val = (mean_values - sd_values).min()
    max_val = (mean_values + sd_values).max()
    
    # create custom y axis labels
    dimension = dict(
        range=[min_val, max_val],
        label=label_map[metric],
        values=filtered_df[metric],
        tickvals=np.linspace(min_val, max_val, 5),
        ticktext=[f"{val:.1f}" for val in np.linspace(min_val, max_val, 5)]
    )
    dimensions.append(dimension)

fig = go.Figure(data=
    go.Parcoords(
        line=dict(
            color=df.index,
            colorscale=[[i/(len(filtered_df)-1), color] for i, color in enumerate(filtered_df['color'])],
            showscale=False,
            cmin=0,
            cmax=len(filtered_df)-1
        ),
        unselected=dict(
            line=dict(
                opacity=0.9 
            )
        ),
        dimensions=dimensions,
        labelangle=30,
        labelfont=dict(size=14),
    )
)

# Update layout
fig.update_layout(
    title={
        'text': "Environmental Impact of Different Diet Types",
        'y': 0.95,            
        'x': 0.5,             
        'xanchor': 'center',  
        'yanchor': 'top',     
        'font': {
            'size': 24,       
            'family': 'Arial', 
            'color': 'black'
        },
        'pad': {
            'b': 30,          
            't': 10           
        }
    },
    font=dict(size=12),
    height=650,              
    width=1200,
    margin=dict(l=120, r=80, t=200, b=120), 
    paper_bgcolor='white',    
    plot_bgcolor='white',     
    template='plotly_white',   
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        showline=False,
        title=None
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        showline=False,
        title=None
    ),
)

# order of legend
group_set = ['vegan', 'veggie', 'fish', 'meat', 'meat50', 'meat100']
for diet in group_set:
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(
                size=12,
                color=colors[diet],
                symbol='circle',
                line=dict(width=1, color='rgba(0,0,0,0.3)')
            ),
            name=diet,
            showlegend=True
        )
    )

# bottom legend
fig.update_layout(
    legend=dict(
        orientation="h",          
        yanchor="bottom",         
        y=-0.2,                   
        xanchor="center",         
        x=0.5,                    
        font=dict(size=14),       
        itemsizing='constant',    
        itemwidth=70,             
        bgcolor='rgba(255,255,255,0.7)',  
        bordercolor='rgba(0,0,0,0.2)',
        borderwidth=1
    )
)

# add annotation for which mc run is selected
fig.add_annotation(
    x=1.0, 
    y=0.95, 
    xref="paper", 
    yref="paper", 
    text=f"<b>MC Run Selected</b><br>{','.join([str(id) for id in selected_mc_run_ids])}",
    showarrow=False,
    align="left",
    bordercolor="black",
    borderwidth=1,
    borderpad=4,
    bgcolor="white",
    opacity=0.8
)

# fig.show()

fig.write_html(
    "full_set_diet_parallel_coordinates.html", 
    include_plotlyjs=True,
    full_html=True,
    config={
        'displayModeBar': True,
        'responsive': True
    }
)

# Add custom centering CSS to center plot
with open("full_set_diet_parallel_coordinates.html", "r") as f:
    html_content = f.read()

centered_html = html_content.replace(
    '</head>',
    '''<style>
    body {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        margin: 0;
        padding: 0;
        background-color: white;
    }
    .plotly-graph-div {
        margin: 0 auto;
        background-color: white !important;
    }
    .js-plotly-plot .plotly .bg {
        fill: white !important;
    }
    /* Make the data lines appear thicker */
    /* Target all data line elements */
    .js-plotly-plot .parcoords .lines path {
        stroke-width: 6px !important;
        vector-effect: non-scaling-stroke !important;
    }
    
    /* Target individual line groups */
    .js-plotly-plot .parcoords .lines {
        stroke-width: 6px !important;
    }
    
    /* Target the connecting paths */
    path.connect {
        stroke-width: 6px !important;
    }
    </style>
    </head>'''
)

with open("full_set_diet_parallel_coordinates.html", "w") as f:
    f.write(centered_html)
