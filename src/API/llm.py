import requests
import json
from history import History, Message, merge_histories

class LLM:
    def ask(self, history: History):
        raise NotImplementedError

import os
from database_json import parse_history_from_json_learning_format

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
    back_hist = parse_history_from_json_learning_format(f'data/learning/learning_data_{model_name}.json')
    return model.ask(merge_histories(back_hist, history))


if __name__ == '__main__':
    QWEN_API_KEY = "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"
    history = History([Message('user', 'Привет, братан')])
    model = QwenLLM(QWEN_API_KEY)
    print(ask_model(model, 'test', history))