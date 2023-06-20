import flask
import dash
from dash import dcc, html, Input, Output, State
import os
import json
import tempfile

from src.md_json2sqlite import main
from apputils import b64_to_pil

# Create temp folder for image upload
UPLOAD_FOLDER = tempfile.mkdtemp(dir=os.getcwd())

# Object to be returned
OUTPUT_OBJECT="detection_db.sqlite"

# Application 
app = dash.Dash(__name__)
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
    html.A('Download Results', id='download-button', href='', download='list_of_detections.json', target='_blank')
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

    md_analyse(UPLOAD_FOLDER, "list_of_detections.json")
    to_sqlite("list_of_detections.json", "detection_db.sqlite")

    return "Analysis completed successfully, you can now download the results"


@app.callback(
    Output('download-button', 'href'),
    Input('download-button', 'n_clicks'),
    State('results-output', 'children')
)
def generate_download_link(n_clicks, results):
    if results is not None:
        # Return the download link to update the href attribute of the download-button
        download_link = f'/download?filename={OUTPUT_OBJECT}'
        return download_link

    # If no results are available, return an empty href
    return ''


@app.server.route('/download')
def download():
    # Get the filename from the query parameters
    filename = flask.request.args.get('filename')

    # Generate the file path to the JSON file
    file_path = os.path.join(os.getcwd(), filename)

    # Return the JSON file for download
    return flask.send_file(file_path, mimetype='application/sqlite', as_attachment=True)

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8999, debug=True)