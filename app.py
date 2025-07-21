from pathlib import Path
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, dash_table
from dash import Input, Output
import dash
import os

url = f"https://docs.google.com/spreadsheets/d/14BmPMe3MQmgVpenBTjPv9QPTF3LIVIej_AQbrzEmUdw/export?" \
      f"format=csv&gid=0"
cohort_normalized = pd.read_csv(url)

cohort_normalized = cohort_normalized.set_index(["segment","subcategory"])

for col in cohort_normalized.columns:
    cohort_normalized[col] = pd.to_numeric(cohort_normalized[col], downcast='float')

############dashboard#####################


# Scale and format numeric columns
value_cols = cohort_normalized.columns
df_percent = cohort_normalized.copy()

for col in value_cols:
    df_percent[col] = cohort_normalized[col] * 100

df_percent.reset_index(inplace=True)

# Prepare conditional color formatting based on value ranges
style_data_conditional = []

# Create a gradient from red (0%) to green (100%)
for col in value_cols:
    style_data_conditional.append({
        'if': {
            'column_id': col,
            'filter_query': '{{{}}} >= 30'.format(col)
        },
        'backgroundColor': '#b4e6a3', 'color': 'black'
    })
    style_data_conditional.append({
        'if': {
            'column_id': col,
            'filter_query': '{{{}}} >= 15 && {{{}}} < 30'.format(col, col)
        },
        'backgroundColor': '#f2fea9', 'color': 'black'
    })

    style_data_conditional.append({
        'if': {
            'column_id': col,
            'filter_query': '{{{}}} >= 5 && {{{}}} < 15'.format(col, col)
        },
        'backgroundColor': '#f9d387', 'color': 'black'
    })
    style_data_conditional.append({
        'if': {
            'column_id': col,
            'filter_query': '{{{}}} >0 && {{{}}} < 5'.format(col, col)
        },
        'backgroundColor': '#fea9a9', 'color': 'black'
    })


# Create Dash app
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("Cohort Table - by Subcategory", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='segment-filter',
        options=[{'label': s, 'value': s} for s in sorted(df_percent['segment'].unique())],
        placeholder='Select Segment',
        style={'width': '300px', 'marginBottom': '20px'}
    ),
    dcc.Dropdown(
    id='subcategory-filter',
    options=[{'label': s, 'value': s} for s in sorted(df_percent['subcategory'].unique())],
    placeholder='Select Subcategory',
    style={'width': '300px', 'marginBottom': '20px'}
),

    dash_table.DataTable(
         id='cohort-table',
        data=df_percent.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in df_percent.columns],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'center',
            'minWidth': '100px',
            'maxWidth': '180px',
            'whiteSpace': 'normal',
        },
        style_data_conditional=style_data_conditional,
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        fixed_rows={'headers': True},
        page_size=100
    )
])

@app.callback(
    Output('cohort-table', 'data'),
    Input('segment-filter', 'value'),
    Input('subcategory-filter', 'value')
)
def update_table(selected_segment, selected_subcategory):
    filtered_df = df_percent.copy()
    
    if selected_segment:
        filtered_df = filtered_df[filtered_df['segment'] == selected_segment]
    
    if selected_subcategory:
        filtered_df = filtered_df[filtered_df['subcategory'] == selected_subcategory]

    return filtered_df.to_dict('records')

if __name__ == "__main__":
    app.run(debug=True)
    port = int(os.environ.get("PORT", 8050))
