import base64

from flask import request, jsonify
from ultralytics import YOLO
from PIL import Image
from ticket import add_ticket_object
from datetime import datetime

from llm import ask_model_promt_image
from app import app, model
from config import PROMPT

@app.route('/get_pred_qwen', methods=['GET'])
def get_pred():
    try:
        base64_image = request.files['image'].stream.read().decode('utf-8')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    global model, PROMPT
    model_ans = ask_model_promt_image(model, 'test', PROMPT, base64_image)
    return model_ans, 200

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
        user_id = int(request.args.get('user_id'))
        format_string = "%Y-%m-%d %H:%M:%S.%f"
        time_str = request.args.get('user_time')
        user_time = datetime.strptime(time_str, format_string)
    except Exception as e:
        return jsonify({"context": "Invalid or missing parameters", "error":e}), 400

    # Кодируем в base64 и декодируем в обычную строку
    img_str = base64.b64encode(file.read()).decode("utf-8")

    add_ticket_object(user_lat=lat,user_lon=lon,
                      user_id=user_id,
                      user_time=user_time,
                      user_photo=img_str)
    return jsonify({'status':'Ok.'}), 200