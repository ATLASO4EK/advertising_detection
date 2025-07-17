import requests
import json
from history import History, Message, merge_histories
from database import parse_history_from_json_learning_format
from features import str_to_dict

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


# Список признаков и соответствующих json-файлов
PRIZNAK_MODELS = {
    "height": "data/learning/learning_data_height.json",
    "axis": "data/learning/learning_data_axis.json",
    "table_height": "data/learning/learning_data_table_height.json",
    "table_location": "data/learning/learning_data_table_location.json",
    "content_area": "data/learning/learning_data_content_area.json",
    "alignment": "data/learning/learning_data_alignment.json",
    "letters_area": "data/learning/learning_data_letters_area.json",
    "roof_offset": "data/learning/learning_data_roof_offset.json",
    "satellite": "data/learning/learning_data_satellite.json",
    "logo_only": "data/learning/learning_data_logo_only.json",
    "no_extra_info": "data/learning/learning_data_no_extra_info.json",
    "lightbox_info": "data/learning/learning_data_lightbox_info.json",
    "horizontal_text": "data/learning/learning_data_horizontal_text.json",

}

def get_priznak_models(api_key):
    models = {}
    for name, path in PRIZNAK_MODELS.items():
        base_model = QwenLLM(api_key)
        models[name] = get_learning_llm_from_data(base_model, path)
    return models

def get_priznak_results(models, history):
    results = {}
    for name, model in models.items():
        result = model.ask(history)
        results[name] = result.strip().lower()
    return results

def get_final_decision(api_key, priznak_results):
    # Формируем историю для генеральной модели
    prompt = str(priznak_results)
    history = History([Message('user', prompt)])
    general_model = get_learning_llm_from_data(QwenLLM(api_key), "data/learning/learning_data_general.json")
    return general_model.ask(history)


QWEN_API_KEY = "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"


def correct_ask_model(model: LLM, history: History, correct_answer: str):
    model_answer = model.ask(history)
    model_answer = model_answer.replace("```", "").replace("json", "")
    print(model_answer)

    try:
        madict = str_to_dict(model_answer)
        result = madict['result']
    except:
        result = model_answer

    if result == correct_answer:
        return 1
    return 0

def get_answer(image_path):
    history_with_image = History([Message('user', None, Message.encode_image(image_path))])

    qwen_kronchtein = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_kronchtein.json")    
    if not correct_ask_model(qwen_kronchtein, history_with_image, "YES"):
        return 1
    
    qwen_height = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_height.json")    
    if not correct_ask_model(qwen_height, history_with_image, "да"):
        return 0

    qwen_unecc_info = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_no_extra_info.json")
    if not correct_ask_model(qwen_unecc_info, history_with_image, "нет"):
        return 0
    
    # есть ли вывеска на фото
    qwen_board = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_board.json")
    if not correct_ask_model(qwen_board, history_with_image, "YES"):
        return 1 # если вывески нет - значит все ок
    
    qwen_similar_line = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_axis.json")
    if not correct_ask_model(qwen_similar_line, history_with_image, "да"):
        return 0

    return 1
        


if __name__ == '__main__':


    image_path = "data/images/img36.jpg"
    
    # history_with_image = History([Message('user', None, Message.encode_image(image_path))])
    # qwen_board = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_kronchtein.json")
    # if not correct_ask_model(qwen_board, history_with_image, "YES"):
    #     print(1)

    print(get_answer(image_path))



    # priznak_models = get_priznak_models(QWEN_API_KEY)
    # priznak_results = get_priznak_results(priznak_models, history)
    # final_decision = get_final_decision(QWEN_API_KEY, priznak_results)

    # print("Результаты по признакам:", priznak_results)
    # print("Итоговое решение:", final_decision)
