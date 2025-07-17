from datetime import datetime
import requests

def send_photo_to_api(user_id, photo_bytes, lat=None, lon=None):
    # Отправка фото и координат на локальный сервер
    url = 'http://web:5000/get_pred_qwen'
    files = {'image':photo_bytes}
    try:
        response = requests.get(url, files=files, timeout=60)
        print(f"API response for user {user_id}: {response.status_code} {response.text}")
        return response.json()
    
    except Exception as e:
        print(f"Ошибка при отправке на API: {e}")
        return None

def post_ticket(user_id, photo_bytes, lat, lon):
    """
    Создает POST-запрос в API для сохранения тикета в БД
    """
    # id, create_time, user_id, user_photo, user_lat, user_lon, user_time, notFake
    url = 'http://web:5000/ticket'
    files = {'image':photo_bytes}
    params = {}
    params['lat'] = str(lat)
    params['lon'] = str(lon)
    params['user_id'] = int(user_id)
    params['user_time'] = datetime.now()

    try:
        response = requests.post(url, files=files, params=params, timeout=30)
        print(f"API response for user {user_id}: {response.status_code} {response.text}")
        return response.json()

    except Exception as e:
        print(f"Ошибка при отправке на API: {e}")
        return None