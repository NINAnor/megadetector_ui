import flask
import dash
import dash_bootstrap_components as dbc
import os
import json
import tempfile
import time
import shutil

from dash import dcc, html, Input, Output, State

from src.md_json2sqlite import main
from apputils import b64_to_pil, md_analyse, to_sqlite, visualise_bbox

# Create temp folder for image upload
UPLOAD_FOLDER = tempfile.mkdtemp(dir=os.getcwd())

# Create a temp folder for storing the images with the bbox drawn
BBOX_FOLDER = tempfile.mkdtemp(dir=os.getcwd())

# Object to be returned
OUTPUT_OBJECT="detection_db.sqlite"

# Instructions as a list:
instr= ["Click on the Drag and Drop box below to upload the pictures to be analysed", 
        "Once this is done click on button 'Analyze'. You should see a spinner indicating that the images are being analyzed.",
        "Once the spinner disappears you will be able to click on the button 'Download' to get the results as an 'SQLite' database."]

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
    html.Div(id='output-message', style={'justifyContent': 'center'}) 
])

@app.callback(
    Output('results-output', 'children'),
    Output('output-message', 'children'),
    Input('analyze-button', 'n_clicks'),
    State('folder-upload', 'contents'),
    Input('folder-upload', 'filename')
)
def analyze_folder(n_clicks, contents, filenames):
    if not filenames or not contents:
        return " ", " "

    for filename, content in zip(filenames, contents):
        # Image is encoded in base64
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        string = content.split(';base64,')[-1]
        img = b64_to_pil(string)
        img.save(temp_path)

    if n_clicks >= 1:
        # Initial message to activate the spinner
        time.sleep(2)  # simulation of delay
        output_message = "Analyzing ..."
        
        md_analyse(UPLOAD_FOLDER, "list_of_detections.json")
        to_sqlite("list_of_detections.json", "detection_db.sqlite")

        # A delay to simulate the analysis
        time.sleep(2)  # simulation of delay
        output_message = "Images have been properly analysed, you can now download the results"

        return " ", output_message
    
    return " ", " "

@app.callback(
    Output('download-db', 'data'),
    Input('download-button', 'n_clicks')
)
def dl_db(n_clicks):
    if n_clicks==1:
        if os.path.exists(OUTPUT_OBJECT):
            return dcc.send_file(OUTPUT_OBJECT)
        else:
            return "No database has been created"
        
@app.callback(
        Output('download-pics', 'data'),
        Input('download-pics-button', 'n_clicks')
)
def dl_bbox_pics(n_clicks):
    if n_clicks==1:
        visualise_bbox("list_of_detections.json", BBOX_FOLDER, UPLOAD_FOLDER)
        shutil.make_archive('processed_pics.zip', 'zip', BBOX_FOLDER)
        if os.path.exists('processed_pics.zip'):
            return dcc.send_file('processed_pics.zip')
        else:
            return "No pictures have been processed"

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8999, debug=True)