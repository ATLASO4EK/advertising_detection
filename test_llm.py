from llm import *
from llm_tree import *

TEST_GROUND_TRUTH = {
    "img0.jpg": 1,
    "img1.jpg": 0,
    "img2.jpg": 0,
    "img3.jpg": 0,
    "img4.jpg": 0,
    "img5.jpg": 1,
    "img6.jpg": 0,
    "img7.jpg": 0,
    "img8.jpg": 0,
    "img9.jpg": 0,
    "img10.jpg": 0,
    "img11.jpg": 0,
    "img12.jpg": 1,
    "img13.jpg": 0,
    "img14.jpg": 0,
    "img15.jpg": 0,
    "img16.jpg": 0,
    "img17.jpg": 1,
    "img18.jpg": 0,
    "img19.jpg": 0,
    "img20.jpg": 0,
    "img21.jpg": 0,
    "img22.jpg": 0,
    "img23.jpg": 0,
    "img24.jpg": 0,
    "img25.jpg": 1,
    "img26.jpg": 0,
    "img27.jpg": 0,
    "img28.jpg": 0,
    "img29.jpg": 0,
    "img30.jpg": 1,
    "img31.jpg": 0,
    "img32.jpg": 0,
    "img33.jpg": 0,
    "img34.jpg": 0,
    "img35.jpg": 0,
    "img36.jpg": 0,
    "img37.jpg": 0,
    "img38.jpg": 0,
    "img39.jpg": 0,
    "img40.jpg": 0,
    "img41.jpg": 0,
    "img42.jpg": 1,
    "img43.jpg": 0,
    "img44.jpg": 0,
    "img45.jpg": 0,
    "img46.jpg": 0,
    "img47.jpg": 0,
    "img48.jpg": 0,
    "img49.jpg": 1,
}

def evaluate_model_accuracy(model, image_ids=None):
    """
    Evaluate model accuracy on test images
    Args:
        image_ids: Optional list of image IDs to evaluate. If None, uses all images from TEST_GROUND_TRUTH
    Returns:
        float: Accuracy score (0.0 to 1.0)
    """
    if image_ids is None:
        image_ids = list(TEST_GROUND_TRUTH.keys())
    
    correct = 0
    total = 0
    
    for img_id in image_ids:
        image_path = f"data/images/{img_id}"
        history_with_image = History([Message('user', None, Message.encode_image(image_path))])

        try:
            prediction = correct_ask_model(model, history_with_image, 'yes')
            if prediction == TEST_GROUND_TRUTH[img_id]:
                correct += 1
            total += 1

            print(f"Image: {img_id}, Predicted: {prediction}, Actual: {TEST_GROUND_TRUTH[img_id]}")

        except Exception as e:
            print(f"Error processing {img_id}: {str(e)}")
            continue
    
    accuracy = correct / total if total > 0 else 0
    print(f"\nOverall Accuracy: {accuracy:.2%}")
    return accuracy

if __name__ == '__main__':
    # Evaluate model on test set

    qwen_board = get_learning_llm_from_data(QwenLLM(QWEN_API_KEY), "data/learning/learning_data_kronchtein.json")
    evaluate_model_accuracy(qwen_board, [f"img{i}.jpg" for i in range(0, 10)])

    # Test single image
    # image_path = "data/images/img36.jpg"
    # print(get_answer(image_path))



    # priznak_models = get_priznak_models(QWEN_API_KEY)
    # priznak_results = get_priznak_results(priznak_models, history)
    # final_decision = get_final_decision(QWEN_API_KEY, priznak_results)

    # print("Результаты по признакам:", priznak_results)
    # print("Итоговое решение:", final_decision)
