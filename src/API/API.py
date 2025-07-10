from flask import Flask, request, jsonify
from ultralytics import YOLO
from PIL import Image
from db import Session, CityObject
import asyncio
import base64
import io
from ticket import add_ticket_object
import numpy as np
import torch
import torchvision
from torch import nn
from torchvision import transforms as tr
from torchvision.models import vit_h_14
from math import sqrt


app = Flask(__name__)   # Создаем API
YOLO_model = YOLO('src/API/YOLO.pt')     # Загружаем дообученную YOLO для детекции граффити и рекламы

device = 'cuda' if torch.cuda.is_available() else 'cpu'
wt = torchvision.models.ViT_H_14_Weights.DEFAULT
model = vit_h_14(weights=wt)


# Проверка подлинности фото
def cosine_similarity(img1, img2):
    global model
    model.heads = nn.Sequential(*list(model.heads.children())[:-1])
    model = model.to(device)
    img1 = process_test_image(img1, device)
    img2 = process_test_image(img2, device)
    emb_one = model(img1).detach().cpu()
    emb_two = model(img2).detach().cpu()
    scores = torch.nn.functional.cosine_similarity(emb_one, emb_two)
    return scores.numpy().tolist()

# Подготавливаем изображение к проверке на подлинность
def process_test_image(img, device):
    transformations = tr.Compose([tr.ToTensor(),
                                  tr.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
                                  tr.Resize((518, 518))])
    img = transformations(img).float()
    img = img.unsqueeze_(0)

    img = img.to(device)

    return img


# Ищем ближайший объект по евклидову расстоянию
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

# Сравниваем с объектами в бд
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

# Получение только class:bb
@app.route('/get_boxes', methods=['GET'])
def get_boxes():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400

    try:
        file = request.files['image']
        img = Image.open(file.stream)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    results = YOLO_model.predict([img])
    response = {}
    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        for i in range(len(boxes.cls)):
            response.update({int(boxes.cls[i].item()):list(boxes.xywh[i].tolist())})

    return response

# Общий анализ фото
@app.route('/analyze', methods=['GET'])
async def analyze():
    '''
    Анализирует изображение на наличие рекламы или граффити,
    проводя проверки на фрод, и с учетом геолокации

    Для запроса
    в качестве файла необходимо передать open('img, 'rb'),
    в качестве параметров lat и lon - географические координаты фотографии (PIL Image)
    :return:    dict{int(class):list(xywh of bounding box)}
    '''

    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400
    try:
        file = request.files['image']
        img = Image.open(file.stream)
    except (TypeError, ValueError):
        return jsonify({'error': "Invalid or missing image"}), 400
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing coordinates"}), 400

    closest_obj = await asyncio.to_thread(find_closest_object, Session(), lat, lon)

    if not closest_obj:
        closest_obj = None
    else:
        closest_obj_photo = Image.open(io.BytesIO(base64.b64decode(closest_obj.to_dict()['photo'].encode())))

    if closest_obj:
        similarity = cosine_similarity(closest_obj_photo, img)[0]
    else:
        similarity = 1.0

    if similarity >= 0.5:
        results = YOLO_model.predict([img])
        response = {}
        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            for i in range(len(boxes.cls)):
                response.update({int(boxes.cls[i].item()): list(boxes.xywh[i].tolist())})

        return jsonify({"notFake":True,
                        "predictions":response}), 200
    # Костыль, тк малая БД
    else:
        results = YOLO_model.predict([img])
        response = {}
        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            for i in range(len(boxes.cls)):
                response.update({int(boxes.cls[i].item()): list(boxes.xywh[i].tolist())})

        return jsonify({"notFake": False,
                        "predictions": response}), 200
    # Как должно быть
    '''
    else:
        return jsonify({"error": "Fake or invalid image"}), 400
    '''

# Создаем тикет
@app.route('/ticket', methods=['POST'])
async def ticket():
    """
    Создает тикет на очистку места от граффити или рекламы (сохранение в БД)
    """
    # id, create_time, user_id, user_photo, user_lat, user_lon, user_time, notFake

    try:
        file = request.files['image']
        img = Image.open(file.stream)
    except (TypeError, ValueError):
        return jsonify({'error': "Invalid or missing image"}), 400

    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        create_time = int(request.args.get('lon'))
        user_id = int(request.args.get('lon'))
        user_time = int(request.args.get('lon'))
        notFake = bool(request.args.get('lon'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing parameters"}), 400

    add_ticket_object(create_time=create_time,
                      user_lat=lat,user_lon=lon,
                      user_id=user_id,
                      user_time=user_time,
                      not_fake=notFake,
                      user_photo=img)

    return 200


app.run(debug=True)

