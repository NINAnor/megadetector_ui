import flask
import dash
import dash_bootstrap_components as dbc
import dash.exceptions as dex
import os
import json
import tempfile
import time
import shutil

from dash import dcc, html, Input, Output, State

from src.md_json2sqlite import main

# Backend functions
from apputils import b64_to_pil, md_analyse, to_sqlite, visualise_bbox
# Frontend functions
from apputils import alert_msg, info_msg

# Create temp folder for image upload
UPLOAD_FOLDER = tempfile.mkdtemp(dir=os.getcwd())

# Create a temp folder for storing the images with the bbox drawn
BBOX_FOLDER = tempfile.mkdtemp(dir=os.getcwd())

# Object to be returned
OUTPUT_OBJECT="detection_db.sqlite"

# Instructions as a list:
instr= ["Click on the Drag and Drop box below to upload the pictures to be analysed", 
        "Once this is done click on button 'Analyze'. You should see a spinner indicating that the images are being analyzed.",
        "Once the spinner disappears you will be able to click on the button 'Download' to get the results as an 'SQLite' database.",
        "It is also possible to download the processed images (i.e. displaying the bounding box by clicking on the button 'Download labelled pics')"]

# Application 
app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = 'MegaDetector Analysis Dashboard'

app.layout = html.Div([
    html.H1('MegaDetector Analysis Dashboard'),
    html.Ul(id="instructions", children=[html.Li(i) for i in instr]),
    dcc.Upload(
        id='folder-upload',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select files')
        ]),
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
        },
        multiple=True
    ),
    html.Div(
        children=[
            html.Button('Analyze', id='analyze-button', n_clicks=0),
            dcc.Loading(id="loading", children=[html.Div(id='results-output')], type="circle", style={'marginTop': '80px'}), 
            html.Button('Download DB', id="download-button", n_clicks=0),
            html.Button('Download labelled pics', id='download-pics-button', n_clicks=0)
        ],
        style={'display': 'flex', 'justifyContent': 'center'}
    ),
    dcc.Download(id="download-db"),
    dcc.Download(id="download-pics"),

    # Add the error messages Div
    html.Div(id='info-msg', style={'justifyContent': 'center'}),
    html.Div(id='alert-message-bbox', style={'justifyContent': 'center'}),
    html.Div(id='alert-message-db', style={'justifyContent': 'center'}),
    html.Div(id='alert-msg-pics', style={'justifyContent': 'center'})
])

@app.callback(
    Output('results-output', 'children'),
    Output('alert-msg-pics', 'children'),
    Output('info-msg', 'children'),
    Input('analyze-button', 'n_clicks'),
    State('folder-upload', 'contents'),
    Input('folder-upload', 'filename'),
    State('info-msg', 'children'),
    State('alert-msg-pics', 'children')
)
def analyze_folder(n_clicks, contents, filenames, info_m, alert_pics):
    if not filenames or not contents:
        if n_clicks >= 1:
            alert_message = alert_msg("No images have been found, please upload some images")
            if alert_message and 'error-alert.dismissed' in dash.callback_context.triggered[0]['prop_id']:
                return None, html.Div(), html.Div()   # Dismiss the alert message
            return html.Div(), alert_message, html.Div() 
        else:
            return '', '', ''

    for filename, content in zip(filenames, contents):
        # Image is encoded in base64
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        string = content.split(';base64,')[-1]
        img = b64_to_pil(string)
        img.save(temp_path)

    if n_clicks >= 1:
        
        time.sleep(2)  # simulation of delay

        md_analyse(UPLOAD_FOLDER, "list_of_detections.json")
        to_sqlite("list_of_detections.json", "detection_db.sqlite")

        time.sleep(2)  # simulation of delay
        info_m = info_msg("The images have been successfully analyzed! You can now download the result.")

        if info_m and 'info-alert.dismissed' in dash.callback_context.triggered[0]['prop_id']:
            return None, html.Div(), html.Div()   # Dismiss the alert message

        return html.Div(), html.Div() , info_m
    
    return html.Div(), html.Div(), html.Div() 

@app.callback(
    Output('download-db', 'data'),
    Output('alert-message-db', 'children'),
    Input('download-button', 'n_clicks'),
    State('alert-message-db', 'children')  # Use State instead of Input for output-message
)
def dl_db(n_clicks, alert_message_db):
    if n_clicks>=1:
        if os.path.exists(OUTPUT_OBJECT):
            return dcc.send_file(OUTPUT_OBJECT), ''
        else:
            alert_message = alert_msg("Pictures have not been processed -> Database can not be found")

            if alert_message and 'error-alert.dismissed' in dash.callback_context.triggered[0]['prop_id']:
                return None, html.Div()  # Dismiss the alert message

            return None, alert_message
        
    return None, html.Div()
        
@app.callback(
        Output('download-pics', 'data'),
        Output('alert-message-bbox', 'children'),
        Input('download-pics-button', 'n_clicks'),
        State('alert-message-bbox', 'children')  # Use State instead of Input for output-message
)
def dl_bbox_pics(n_clicks, alert_message_bbox):
    if n_clicks>=1:
        if os.path.exists("list_of_detections.json"):
            visualise_bbox("list_of_detections.json", BBOX_FOLDER, UPLOAD_FOLDER)
            zip_filename = shutil.make_archive('processed_pics', 'zip', BBOX_FOLDER)
            return dcc.send_file(zip_filename), html.Div()
        else:
            alert_message = alert_msg("Pictures have not been processed -> Labelled pictures cannot be downloaded")

            if alert_message and 'error-alert.dismissed' in dash.callback_context.triggered[0]['prop_id']:
                return None, html.Div()  # Dismiss the alert message

            return None, alert_message
    return None, html.Div()
        
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8999, debug=True)