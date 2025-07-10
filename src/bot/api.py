import requests

def send_photo_to_api(user_id, photo_bytes, lat=None, lon=None):
    # Отправка фото и координат на локальный сервер
    url = 'http://127.0.0.1:5000/analyze'
    files = {'image': ('photo.jpg', photo_bytes, 'image/jpeg')}
    params = {}
    if lat is not None:
        params['lat'] = str(lat)
    if lon is not None:
        params['lon'] = str(lon)
    try:
        response = requests.get(url, files=files, params=params, timeout=30)
        print(f"API response for user {user_id}: {response.status_code} {response.text}")
        return response.json()
    
    except Exception as e:
        print(f"Ошибка при отправке на API: {e}")
        return None