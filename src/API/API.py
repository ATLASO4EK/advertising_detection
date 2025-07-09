import io

from flask import Flask
from ultralytics import YOLO
import base64
from PIL import Image

app = Flask(__name__)
model = YOLO('YOLO.pt')

@app.route('/get_boxes/<img>')
def get_boxes(img=None):
    if img==None:
        return 'No Image', 404
    results = model.predict([Image.open(io.BytesIO(base64.b64decode(img)))])
    response = {}
    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        for i in range(len(boxes.cls)):
            response.update({int(boxes.cls[i]):list(boxes.xywh[i])})

    return response, 200

if __name__ == 'main':
  app.run(debug=True)