import io
from flask import Flask
from ultralytics import YOLO
import base64
from PIL import Image
import os


app = Flask(__name__)
model = YOLO('src/API/YOLO.pt')

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/abduz/<name>')
def he_world(name):
  return f'Hello, World! {name}'

@app.route('/get_boxes/<img>')
def get_boxes(img):
    #return io.BytesIO(base64.urlsafe_b64decode(img))
    results = model.predict([Image.open(io.BytesIO(base64.urlsafe_b64decode(img)))])
    response = {}
    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        for i in range(len(boxes.cls)):
            response.update({int(boxes.cls[i]):list(boxes.xywh[i])})

    return response

app.run(debug=True)