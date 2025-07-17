from llm import *

def correct_ask_model(model: LLM, history: History, correct_answer: str):
    model_answer = model.ask(history)
    model_answer = model_answer.replace("```", "").replace("json", "")
    print(model_answer)

    try:
        madict = str_to_dict(model_answer)
        result = madict['result'].lower()
    except:
        result = model_answer.lower()

    if result == correct_answer:
        return 1
    return 0

def get_answer(image_path):
    history_with_image = History([Message('user', None, Message.encode_image(image_path))])

    # есть ли вывеска с кронштейном на фото
    qwen_kronchtein = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_kronchtein.json")    
    if not correct_ask_model(qwen_kronchtein, history_with_image, "YES"):
        return 1
    
    # находится ли вывеска с кронштейном на высоте  >2.5метров от земли 
    qwen_height = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_height.json")    
    if not correct_ask_model(qwen_height, history_with_image, "да"):
        return 0
    
    # содержит ли вывеска с кронштейном лишнюю информацию
    qwen_unecc_info = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_no_extra_info.json")
    if not correct_ask_model(qwen_unecc_info, history_with_image, "нет"):
        return 0
    
    # есть ли вывеска без кронштейна на фото
    qwen_board = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_board.json")
    if not correct_ask_model(qwen_board, history_with_image, "YES"):
        return 1 # если вывески нет - значит все ок
    
    # вывеска без кронштейна и вывеска с кронштейном находятся ли на одной горизонтальной линии
    qwen_similar_line = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_axis.json")
    if not correct_ask_model(qwen_similar_line, history_with_image, "да"):
        return 0

    return 1


if __name__ == '__main__':
    image_path = "data/images/img36.jpg"
    history_with_image = History([Message('user', None, Message.encode_image(image_path))])
    qwen_board = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_kronchtein.json")
    if not correct_ask_model(qwen_board, history_with_image, "YES"):
        print(1)

    print(get_answer(image_path))
