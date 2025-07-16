import requests
import json
from history import History, Message, merge_histories
from database_json import parse_history_from_json_learning_format
from config import LEARNING_HISTORY_DATA_PATH, QWEN_API_KEY, LERNING_HISTORY_NAME_TEMPLATE

class LLM:
    def ask(self, history: History):
        raise NotImplementedError

class QwenLLM(LLM):
    def __init__(self, api_key: str, model: str = "qwen/qwen-vl-plus"):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = model

    def ask(self, history: History):
        messages = history.to_dict()
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
                "messages": messages,
                "max_tokens": 4000
            })
        )
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            print("Ошибка:", response.status_code, response.text)
            return None

def ask_model(model: LLM, model_name: str, history: History):
    back_hist = parse_history_from_json_learning_format(f'{LEARNING_HISTORY_DATA_PATH}{LERNING_HISTORY_NAME_TEMPLATE.format(name = model_name)}')
    return model.ask(merge_histories(back_hist, history))

def ask_model_promt_image(model, model_name, prompt, base64_image):
    message = Message('user', prompt, base64_image)
    history = History([message])
    return ask_model(model, model_name, history)


def test():
    history = History([Message('user', 'Привет, братан')])
    model = QwenLLM(QWEN_API_KEY)
    print(ask_model(model, 'test', history))

if __name__ == '__main__':
    test()