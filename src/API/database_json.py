import json
from history import *  

def parse_JSON(path: str):
    result = {}
    with open(path, 'r', encoding='utf-8') as jsfile:
        result = json.load(jsfile)
    return result

def write_JSON(path: str, js):
    with open(path, 'w', encoding='utf-8') as jsfile:
        result = json.dump(js, jsfile, ensure_ascii=False, indent=4)
    return result


def save_history_to_json(history: History, JSON_PATH: str):
    # Сохраняет History в json-файл в формате, необходимом для API
    messages_json = history.get_messages_json()
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(messages_json, f, ensure_ascii=False, indent=4)
    return True

def parse_history_from_json(JSON_PATH: str) -> History:
    # Читает json-файл (API формат) и преобразует в History
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        messages_data = json.load(f)
    messages = []
    for msg in messages_data:
        role = msg.get('role')
        content = msg.get('content')
        if isinstance(content, list):
            text = None
            base64_image = None
            for item in content:
                if item.get('type') == 'text':
                    text = item.get('text')
                elif item.get('type') == 'image_url':
                    url = item.get('image_url', {}).get('url')
                    if url and url.startswith('data:image/jpeg;base64,'):
                        base64_image = url.split('base64,', 1)[-1]
            messages.append(Message(role=role, text=text, base64_image=base64_image))
        else:
            messages.append(Message(role=role, text=content))
    return History(messages)

def parse_history_from_json_learning_format(JSON_LEARNING_PATH: str) -> History:
    # Читает обучающий json и преобразует в History
    with open(JSON_LEARNING_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    messages = []
    for item in data:
        role = item.get('role')
        text = item.get('text')
        image_path = item.get('image_path')
        base64_image = None
        if image_path:
            try:
                base64_image = Message.encode_image(image_path)
            except Exception:
                base64_image = None
        messages.append(Message(role=role, text=text, base64_image=base64_image))
    return History(messages)
