from datetime import datetime
import requests
from PIL import Image
import base64

def format_qwen_answer(answer: str):
    if answer.lower()[0:13] == 'соответствует':
        return 'соответствует'
    elif answer.lower()[0:11] == 'вывесок нет':
        return 'соответствует'
    elif answer.lower()[0:16] == 'не соответствует':
        return 'не соответствует'

def get_graf_ad(user_id, photo_bytes, lat=None, lon=None):
    # Отправка фото и координат на локальный сервер
    url = 'http://127.0.0.1:5000/get_boxes'
    files = {'image': photo_bytes}
    response = requests.get(url, files=files, timeout=60)
    print(f"API response for user {user_id}: {response.status_code} {response.text}")
    return response.json()

def send_photo_to_api(user_id, photo_bytes, lat=None, lon=None):
    url = 'http://127.0.0.1:5000/get_pred_qwen'
    base64_image = base64.b64encode(photo_bytes).decode('utf-8')
    
    files = {
        'image': ('image.txt', base64_image, 'text/plain')
    }

    response = requests.get(url, files=files, timeout=60)
    print(f"API response for user {user_id}: {response.status_code} {response.text}")
    return format_qwen_answer(response.text)

def post_ticket(user_id, photo_bytes, lat, lon):
    """
    Создает POST-запрос в API для сохранения тикета в БД
    """
    # id, create_time, user_id, user_photo, user_lat, user_lon, user_time, notFake
    url = 'http://127.0.0.1:5000/ticket'
    files = {'image':photo_bytes}
    params = {}
    params['lat'] = str(lat)
    params['lon'] = str(lon)
    params['user_id'] = int(user_id)
    params['user_time'] = datetime.now()

    response = requests.post(url, files=files, params=params, timeout=30)
    return response.json()
