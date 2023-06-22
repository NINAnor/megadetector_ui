import base64
import io
import os

from PIL import Image

from src.md_json2sqlite import main

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
    import subprocess
    subprocess.run(["python", 
                    "/app/CameraTraps/visualization/visualize_detector_output.py", 
                    detection_json, 
                    outfolder, 
                    "-c", "0.8",
                    "-i", infolder])
