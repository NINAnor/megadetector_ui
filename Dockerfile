# Use the base image for python 3.8
FROM python:3.8

# Install the dependancies for cv2
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

# Install poetry (alternative to conda for package management)
RUN pip3 install poetry 

# Install all the poetry dependancies
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

################################
######### TO CORRECT ###########
################################
RUN pip install dash           
RUN pip install tomli           
RUN pip install sqlite-utils
RUN pip install dash-html-components                                         
RUN pip install dash-core-components                                     
RUN pip install plotly
RUN pip install gunicorn openpyxl
RUN pip install dash-bootstrap-components
################################

# Add model.pt in a megadetector folder
RUN mkdir megadetector
ADD https://github.com/microsoft/CameraTraps/releases/download/v5.0/md_v5a.0.0.pt ./megadetector

# Clone the repo megadetector depends on
RUN git clone https://github.com/Microsoft/ai4eutils.git && \
    cd /app/ai4eutils && \ 
    git checkout 9260e6b876fd40e9aecac31d38a86fe8ade52dfd

RUN git clone https://github.com/ultralytics/yolov5.git && \
    cd /app/yolov5 && \ 
    git checkout c23a441c9df7ca9b1f275e8c8719c949269160d1  

RUN git clone https://github.com/microsoft/CameraTraps.git && \
    cd /app/CameraTraps &&  \
    git checkout a1e7c154b43f0982d2f41ffa9359daac666557fb

# Clone the repo that converts the .json file into an sqlite database
RUN git clone https://github.com/NINAnor/md_json2sqlite

# Make a folder for my scripts
COPY ./ /app/


# Change PYTHONPATH
ENV PYTHONPATH "$PYTHONPATH:/app/CameraTraps:/app/ai4eutils:/app/yolov5:/app/md_json2sqlite:/app/utils"

CMD [ "python", "app.py" ]



