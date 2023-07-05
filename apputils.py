import base64
import io
import os
import dash_bootstrap_components as dbc

from PIL import Image

from src.md_json2sqlite import main

#####################
# Backend functions #
#####################
def b64_to_pil(content):
    decoded = base64.b64decode(content)
    buffer = io.BytesIO(decoded)
    img = Image.open(buffer)
    return img

def md_analyse(folder, output_name):
    # Accept a .json file of filenames as input
    os.system(f"python /app/CameraTraps/detection/run_detector_batch.py \
               /app/megadetector/md_v5a.0.0.pt \
              {folder} \
              {output_name}")
    
def to_sqlite(input_json, output_db):
    main(input_json, output_db, False)

def visualise_bbox(detection_json, outfolder, infolder):
    os.system(f"python /app/CameraTraps/visualization/visualize_detector_output.py \
              {detection_json} \
              {outfolder} \
              -i {infolder}")

#######################
# Front-end functions #
#######################
def alert_msg(message):
    alert_message = dbc.Alert(
        message,
        color='danger',
        dismissable=True,
        duration=None,  
        id='error-alert'
    )
    return alert_message

def info_msg(message):
    info_message = dbc.Alert(
        message,
        color='success',
        dismissable=True,
        duration=None,  
        id='info-alert'
    )
    return info_message