import base64
import io
import os

from PIL import Image

from src.md_json2sqlite import main

from utils_ui import info_msg

def copy_temp_imgs(UPLOAD_FOLDER, filenames, contents):
    for filename, content in zip(filenames, contents):
        # Image is encoded in base64
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        string = content.split(';base64,')[-1]
        img = b64_to_pil(string)
        img.save(temp_path)

def analyze_imgs(UPLOAD_FOLDER, list_of_detections, sqlite_db):
    md_analyse(UPLOAD_FOLDER, list_of_detections)
    to_sqlite(list_of_detections, sqlite_db)
    info_m = info_msg("The images have been successfully analyzed! You can now download the result.")
    return info_m

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