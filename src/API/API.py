import io
from flask import Flask, request, jsonify
from ultralytics import YOLO
import base64
from PIL import Image
import os
from db import Session, CityObject
import asyncio


app = Flask(__name__)
model = YOLO('src/API/YOLO.pt')

from math import sqrt

def find_closest_object(db_session, lat: float, lon: float):
    """
    Находит ближайший объект в базе данных к заданным координатам.
    Использует простое евклидово расстояние для примера.
    """
    # Получаем все объекты из БД
    objects = db_session.query(CityObject).all()

    if not objects:
        return None  # Нет объектов в базе

    # Добавляем расстояние и находим ближайший объект
    closest = None
    min_distance = float('inf')

    for obj in objects:
        dx = obj.latitude - lat
        dy = obj.longitude - lon
        distance = sqrt(dx*dx + dy*dy)

        if distance < min_distance:
            min_distance = distance
            closest = obj

    return closest


@app.route('/get_object', methods=['GET'])
async def get_object_by_geo():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing coordinates"}), 400

    closest_obj = await asyncio.to_thread(find_closest_object, Session(), lat, lon)

    if not closest_obj:
        return jsonify({"error": "No objects found in database"}), 404

    return jsonify(closest_obj.to_dict())

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/abduz/<name>')
def he_world(name):
  return f'Hello, World! {name}'

@app.route('/get_boxes', methods=['GET'])
def get_boxes():
    #return io.BytesIO(base64.urlsafe_b64decode(img))
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400

    try:
        file = request.files['image']
        img = Image.open(file.stream)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    results = model.predict([img])
    response = {}
    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        for i in range(len(boxes.cls)):
            response.update({int(boxes.cls[i].item()):list(boxes.xywh[i].tolist())})

    return response

app.run(debug=True)
