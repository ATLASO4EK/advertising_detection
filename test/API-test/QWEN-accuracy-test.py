import pandas as pd
import requests
import os
import base64

root_path = 'C:/Users/Persona/Desktop/advertising_detection-main/test/API-test'
img_path = root_path+'/images'

os.chdir(root_path)

def rename_imgs():
    global root_path
    path = root_path+'/images'
    os.chdir(path)
    file_list = os.listdir()
    for i in range(len(file_list)):
        os.rename(file_list[i], f'img{i}.jpg')

def get_pred(img):
    with open(f'{root_path}/images/{img}', 'rb') as f:
        file = base64.b64encode(f.read()).decode('utf-8')

    url = 'http://127.0.0.1:5000/get_pred_qwen'
    files = {'image': file}
    response = requests.get(url, files=files, timeout=60)

    return response

def prepare_response(response):
    if response.content.decode('utf-8').lower()[0:13] == 'соответствует':
        return 1
    elif response.content.decode('utf-8').lower()[0:11] == 'вывесок нет':
        return 1
    elif response.content.decode('utf-8').lower()[0:16] == 'не соответствует':
        return 0
    else:
        return 404

def get_metrics(path_to_imgs):
    os.chdir(root_path)
    correct_list = list(pd.read_excel('correct.xlsx').iloc[:,1])
    os.chdir(path_to_imgs)
    img_list = os.listdir()
    data = []

    for i in range(len(img_list)):
        pred = prepare_response(get_pred(f'img{i}.jpg'))
        data.append([f'img{i}.jpg', pred, correct_list[i]])
    df = pd.DataFrame(columns=['img', 'pred', 'corr'], data=data)
    df.loc[len(df)] = [None, len(df[df['pred'] == df['corr']]) / len(df), None]
    os.chdir(root_path+'/metrics')
    path_len = len(os.listdir())
    df.to_excel(f'metrics{path_len}.xlsx', index=False)

get_metrics(img_path)