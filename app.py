from pathlib import Path
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.oauth2 import service_account
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, dash_table
from dash import Input, Output
import dash
import os


scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

json_secret = {
  "type": "service_account",
  "project_id": "core-dominion-368514",
  "private_key_id": "5db7e1011629b290acc582de0c70051fe46c909f",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCUWHorL8g9YAoZ\n+BiZ64+WQAj6gKGFNtVDol33Rm6r9JYkGpVurVEXDuSQjGlELMHhKQsz5sdf1JbO\nKVh3IMCKSL4PzAQ681WEG31YUwreY0JfifClAk9uQd15NJZAhy7VL+0UUCF+Obri\nuF3czObbg5em7mNMe/ezZ5iu8d9VoXpfQb5S9+t0l6B2g4sVTpnn4aNqisBp4ILg\n2GACIzl4aUrnPEFBQBok4O7gkCmBCDQxTlUnJNtlTYwhrYmqpqdggGJbvES39UN1\nC0uXIV5T+LNwRg3OLhXhquosJZaoo4b6llPKKD9ozHxCVO2Vo7AWXJLHuVb0VEys\n5l1YpQMfAgMBAAECggEAJDUkPH5BJZnXXVdMyeTQ+x9OEbZrthQYIZXz0XMDeD0O\nmGlUp9rtu+8Koq1i1B0IhWh7L4PYje9Zj6BP02PPGvF+UmS9c5YI/WGoSnKaaIVZ\nofANKHlT4dl5sSfAtKdKKwazmw2j3ydAEi5l2oq4nkOUNE5jNjvbzZIvliO7Gy8b\nc+UUn/winBHPX1DBKJX0cZ389kDx6Sg1XIn7S6IL7pLS1jaqFrNUuHWxzBpFTphl\n834BF7hZi2MUMhYgtiAtGrzXz348ZynCLvajae2KNWx1UtkPCEwAIR3YZYLSSUcF\nxnkWTp1l8AMgbr3rfrCfhYZPhRB3AxI42X+w6PjqwQKBgQDLVagWkUGZd4w7tWPh\nnMd/ihbjDAigZCIbLpIiojqLhWe6BT9qUwQCMiSlqSVBqdlJ5QY3/M+jgTNLSfXf\n1pizHAWcRzOx99BoovmzBt9GoxYhCYlG9eLHo8bnlYmB29jNS9WpcmdSGG7LzJ5G\nE0YB8dsxl3H30f9Xw8RMP0he1wKBgQC6xLXgxyQxuJrMYNdxwWRjzLFcHcHySAfK\nhm8VqKxyiE+0+KATVwGXmXViWJOpSHbcR7y94ceYPURRiDyEDgnu+LetG8xujyMa\n0zU2/np9C30wybtm/cJN98L0IYl0scGWENfkBqZqYO3YochqPHVlEOMdiJ8CIFPe\nozgMvEDc+QKBgBN008utBIjpzopcFf2dod1LWltJaH3odvcA4szblxyInF9JZ0MG\nRIjtQWJ0p/L7jKYsewbacwfjMgRPRG6xuxTQZp0IlyK9YrzQc3I1AyJgMprgrbkT\niCqwOjUosuqxHbKvQfef0dEiM1/e6XotF/LRsLazFh2vg25jdiIRoBwrAoGBAKZy\n/4DnGauyUUtKF1gLOdPzrjFhV+L8LO1iqAeOfrnIH/kyBz+VMBcSrdnLBTY+Hagt\nytkTKhXUrFlZaE1sUZAHW3LMroHt0SRsDSYI39MndRgRAZJFH3DrGXUHmoBElzmN\no0pWXuO5pN+HN5zuatV6ml5MzyFO/FAT+LTo5YnJAoGAWIKkraMPGqNVWPZEHgw3\nFGMQ4C2T2Pj321D7OV60uvBs+Rev9c07xBAF9ZWV5gpVm6k/MlGEr7yOKfjqM/vr\n3QtNLBjzGC4Obx8fsQ9TRyxwWy327bvYQkGasMwBS+/71OqNJEQAKCJyE5w9Sw3g\nftQdUp21B00ST6IWhMjxsmA=\n-----END PRIVATE KEY-----\n",
  "client_email": "analytics@core-dominion-368514.iam.gserviceaccount.com",
  "client_id": "101412732926482857447",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/analytics%40core-dominion-368514.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

credentials = service_account.Credentials.from_service_account_info(json_secret, scopes=scopes)

gc = gspread.authorize(credentials)

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

gs = gc.open_by_key("14BmPMe3MQmgVpenBTjPv9QPTF3LIVIej_AQbrzEmUdw")
sheet = gs.worksheet('Sheet1')

# Get all data as DataFrame
cohort_normalized = pd.DataFrame(sheet.get_all_records())

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
...         data=df_percent.to_dict('records'),
...         columns=[{'name': i, 'id': i} for i in df_percent.columns],
...         style_table={'overflowX': 'auto'},
...         style_cell={
...             'textAlign': 'center',
...             'minWidth': '100px',
...             'maxWidth': '180px',
...             'whiteSpace': 'normal',
...         },
...         style_data_conditional=style_data_conditional,
...         style_header={
...             'backgroundColor': 'rgb(230, 230, 230)',
...             'fontWeight': 'bold'
...         },
...         fixed_rows={'headers': True},
...         page_size=100
...     )
... ])
... 
... @app.callback(
...     Output('cohort-table', 'data'),
...     Input('segment-filter', 'value'),
...     Input('subcategory-filter', 'value')
... )
... def update_table(selected_segment, selected_subcategory):
...     filtered_df = df_percent.copy()
...     
...     if selected_segment:
...         filtered_df = filtered_df[filtered_df['segment'] == selected_segment]
...     
...     if selected_subcategory:
...         filtered_df = filtered_df[filtered_df['subcategory'] == selected_subcategory]
... 
...     return filtered_df.to_dict('records')
... 
... if __name__ == "__main__":
...     --app.run(debug=True)
...     port = int(os.environ.get("PORT", 8050))
