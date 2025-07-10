import requests

def send_photo_to_api(user_id, photo_bytes, lat=None, lon=None):
    # Отправка фото и координат на локальный сервер
    url = 'http://127.0.0.1:5000/analyze'
    files = {'image': photo_bytes}
    params = {}
    if lat is not None:
        params['lat'] = str(lat)
    if lon is not None:
        params['lon'] = str(lon)
    try:
        response = requests.get(url, files=files, params=params, timeout=180)
        print(f"API response for user {user_id}: {response.status_code} {response.text}")
        return response.json()
    
    except Exception as e:
        print(f"Ошибка при отправке на API: {e}")
        return None

def post_ticket(user_id, photo_bytes, lat, lon, create_time, user_time, notFake):
    """
    Создает POST-запрос в API для сохранения тикета в БД
    """
    # id, create_time, user_id, user_photo, user_lat, user_lon, user_time, notFake
    url = 'http://127.0.0.1:5000/analyze'
    files = {'image': photo_bytes}
    params = {}
    params['lat'] = str(lat)
    params['lon'] = str(lon)
    params['user_id'] = int(user_id)
    params['create_time'] = int(create_time)
    params['user_time'] = int(user_time)
    params['notFake'] = bool(notFake)

    try:
        response = requests.post(url, files=files, params=params, timeout=30)
        print(f"API response for user {user_id}: {response.status_code} {response.text}")
        return response.json()

    except Exception as e:
        print(f"Ошибка при отправке на API: {e}")
        return None