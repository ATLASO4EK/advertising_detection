from torch import nn
from torchvision import transforms as tr
from torchvision.models import vit_h_14
from math import sqrt

import torch
import torchvision

from llm import ask_model, History, Message
from database_sql import Session, CityObject

def ask_model_promt_image(model, model_name, prompt, base64_image):
    message = Message('user', prompt, base64_image)
    history = History([message])
    return ask_model(model, model_name, history)

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

def get_start_text():
    with open('src/API/start_prompt.txt', 'r') as f:
        start_text = f.read()
    return start_text