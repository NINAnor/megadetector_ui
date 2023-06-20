import flask
import dash
import dash_bootstrap_components as dbc
import os
import json
import tempfile

from dash import dcc, html, Input, Output, State

from src.md_json2sqlite import main
from apputils import b64_to_pil

# Create temp folder for image upload
UPLOAD_FOLDER = tempfile.mkdtemp(dir=os.getcwd())

# Object to be returned
OUTPUT_OBJECT="detection_db.sqlite"

# Application 
app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = 'MegaDetector Analysis Dashboard'

app.layout = html.Div([
    html.H1('MegaDetector Analysis Dashboard'),
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
            'margin': '10px'
        },
        multiple=True
    ),
    html.Button('Analyze', id='analyze-button', n_clicks=0),
    html.Div(id='results-output'),
    html.Button('Download', id="download-button", n_clicks=0),
    dcc.Download(id="download-db")
])

def md_analyse(json_file, output_name):
    # Accept a .json file of filenames as input
    os.system(f"python /app/CameraTraps/detection/run_detector_batch.py \
               /app/megadetector/md_v5a.0.0.pt \
              {json_file} \
              {output_name}")
    
def to_sqlite(input_json, output_db):
    main(input_json, output_db, False)

@app.callback(
    Output('results-output', 'children'),
    Input('analyze-button', 'n_clicks'),
    State('folder-upload', 'contents'),
    Input('folder-upload', 'filename')
)
def analyze_folder(n_clicks, contents, filenames):
    if not filenames or not contents:
        return "Please upload pictures"
    
    for filename, content in zip(filenames, contents):
        # Image is encoded in base64
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        string = content.split(';base64,')[-1]
        img = b64_to_pil(string)
        img.save(temp_path)

    if n_clicks >= 1:
        md_analyse(UPLOAD_FOLDER, "list_of_detections.json")
        to_sqlite("list_of_detections.json", "detection_db.sqlite")
        return "Images have been properly analysed"

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
    
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8999, debug=True)