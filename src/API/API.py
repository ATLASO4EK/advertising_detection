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
from datetime import datetime
import requests
import json

app = Flask(__name__)   # Создаем API


import requests
import json
import base64

class Message:
    def __init__(self, message=None):
        if message is None:
            message = {}
        self.message = message

    def add_prompt(self, prompt: str):
        self.message = {"role": "user", "content": prompt}

    def add_image(self, base64_image, prompt=None):
        content = []
        if prompt is not None:
            content.append(self.get_text_content(prompt))
        content.append(self.get_image_content(base64_image))
        self.message = {"role": "user", "content": content}

    def encode_image(image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    @staticmethod
    def get_text_content(text):
        return {
            "type": "text",
            "text": text
        }

    @staticmethod
    def get_image_content(base64_image):
        image_type = 'image/jpeg'
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{image_type};base64,{base64_image}"
            }
        }

class History:
    def __init__(self, messages=None):
        if messages is None:
            messages = []
        self.messages = messages

    def get_messages_json(self):
        return [message.message for message in self.messages]

class QWEN:
    def __init__(self, api_key: str, prehistory: History):
        self.prehistory = prehistory.get_messages_json()
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "qwen/qwen-vl-plus"

    def ask(self, messages: History):
        response = requests.post(
            url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://your-app.com",
                "X-Title": "Design Code Checker"
            },
            data=json.dumps({
                "model": self.model,
                "messages": self.prehistory + messages.get_messages_json(),
                "max_tokens": 4000
            })
        )
        if response.status_code == 200:
            data = response.json()
            assistant_reply = data['choices'][0]['message']['content']
            return assistant_reply
        else:
            print("Ошибка:", response.status_code, response.text)
            return None


def ask_model(model, prompt, base64_image):
    message = Message()
    message.add_image(base64_image, prompt)
    history = History([message])
    return model.ask(history)

API_KEY = "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"
prompt = "Проанализируй это изображение на соответствие дизайн-коду города"
with open('src/API/start_prompt.txt', 'r') as f:
    start_text = f.read()
model = QWEN(API_KEY,
    History([
        Message({"role": "system", "content": f"Ты - агент для определения соответствия рекламы дизайн-коду города. (Правилам и нормам). Тебе на вход подается фото объекта. На выходе - json, с ключами:\n'final answer': 'соответствует'/'не соответствует' - твой итоговый ответ\n'pre[i]': 'your_text' - обоснование для i-го пунка из дизайн кода\nВажно, что твой ответ должен быть только в формате json!\nПравила:\n{start_text}\nПример "})]))




# Проверка подлинности фото
def cosine_similarity(img1, img2):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    wt = torchvision.models.ViT_H_14_Weights.DEFAULT
    model = vit_h_14(weights=wt)
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

@app.route('/get_pred_qwen', methods=['GET'])
def get_pred():
    try:
        base64_image = request.files['image'].stream.read().decode('utf-8')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    global model, prompt
    model_ans = ask_model(model, prompt, base64_image)

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

app.run(debug=True)

