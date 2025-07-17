import requests
import json
from history import History, Message, merge_histories
from database import parse_history_from_json_learning_format
from features import str_to_dict
from config import QWEN_API_KEY

class LLM:
    def ask(self, history: History) -> str | None:
        raise NotImplementedError


class LearningLLM(LLM):
    def __init__(self, model: LLM, learning_history: History):
        self.base_model = model
        self.learning_history = learning_history

    def ask(self, history: History):
        return self.base_model.ask(merge_histories(self.learning_history, history))
    
def get_learning_llm_from_data(model, learning_json_path: str) -> LearningLLM:
    learning_history = parse_history_from_json_learning_format(learning_json_path)
    learning_model = LearningLLM(model, learning_history)
    return learning_model


class QwenLLM(LLM):
    def __init__(self, api_key: str, model: str = "qwen/qwen-vl-plus"):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = model

    def ask(self, history: History) -> str | None:
        messages = history.get_messages_json()
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
