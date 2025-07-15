from flask import Flask, request, jsonify
from ultralytics import YOLO
from PIL import Image
from datetime import datetime

import asyncio
import base64
import io

from llm import QwenLLM, History, Message
from database_sql import Session, CityObject
from ticket import add_ticket_object
from config import API_KEY
from features import *

app = Flask(__name__)
model = QwenLLM(API_KEY)
prompt = "Проанализируй это изображение на соответствие дизайн-коду города"


@app.route('/get_pred_qwen', methods=['GET'])
def get_pred():
    try:
        base64_image = request.files['image'].stream.read().decode('utf-8')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    global model, prompt
    model_ans = ask_model_promt_image(model, 'test', prompt, base64_image)

    return model_ans, 200

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

    YOLO_model = YOLO('src/API/YOLO.pt')  # Загружаем дообученную YOLO для детекции граффити и рекламы

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

    if response != {}:
        return jsonify({'status':True,
                        'response':response}), 200
    else:
        return jsonify({'status':False,
                        'response':{}}), 200

# Верификация фото
@app.route('/verify', methods=['GET'])
async def verify():
    return jsonify({'status':'Ok.',
                    'response':{'verified':True}}), 200

# Общий анализ фото (legacy)
@app.route('/legacy/analyze', methods=['GET'])
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

    YOLO_model = YOLO('src/API/YOLO.pt')  # Загружаем дообученную YOLO для детекции граффити и рекламы
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
        inDBobj = False
    else:
        closest_obj_photo = Image.open(io.BytesIO(base64.b64decode(closest_obj.to_dict()['photo'].encode())))

    if closest_obj:
        similarity = cosine_similarity(closest_obj_photo, img)[0]
        inDBobj = True
    else:
        similarity = 1.0
        inDBobj = True

    if similarity >= 0.5:
        results = YOLO_model.predict([img])
        response = {}
        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            for i in range(len(boxes.cls)):
                response.update({int(boxes.cls[i].item()): list(boxes.xywh[i].tolist())})

        notFake=True
    # Костыль, тк малая БД
    else:
        results = YOLO_model.predict([img])
        response = {}
        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            for i in range(len(boxes.cls)):
                response.update({int(boxes.cls[i].item()): list(boxes.xywh[i].tolist())})

        notFake=False

    return jsonify({"notFake": notFake,
                    "similarity":similarity,
                    "geo_similarity":inDBobj,
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        create_time = datetime.now()
        user_id = int(request.args.get('user_id'))
        format_string = "%Y-%m-%d %H:%M:%S.%f"
        time_str = request.args.get('user_time')
        user_time = datetime.strptime(time_str, format_string)
        notFake = int(bool(request.args.get('notFake')))
    except Exception as e:
        return jsonify({"context": "Invalid or missing parameters", "error":e}), 400

    # Кодируем в base64 и декодируем в обычную строку
    img_str = base64.b64encode(file.read()).decode("utf-8")

    add_ticket_object(create_time=create_time,
                      user_lat=lat,user_lon=lon,
                      user_id=user_id,
                      user_time=user_time,
                      not_fake=notFake,
                      user_photo=img_str)

    return jsonify({'status':'Ok.'}), 200

"""

    History([
        Message({"role": "system",
                 "content": f"Ты - агент для определения соответствия рекламы дизайн-коду города. (Правилам и нормам). Тебе на вход подается фото объекта. "
                            f"На выходе - json, с ключами:\n'final answer': 'соответствует'/'не соответствует' - твой итоговый ответ\n"
                            f"'pre[i]': 'your_text' - обоснование для i-го пунка из дизайн кода\nВажно, что твой ответ должен быть только в формате json!"
                            f"\nПравила:\n{get_start_text()}\n"
                            "Пример твоего выхода:\n{'final answer': 'соответствует'}\n"
                            f"Выход должен быть исключительно в таком формате, может содержать больше параметров, но параметр"
                            f"'final answer' должен присутствовать в любом случае"})]))
"""