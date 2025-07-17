import base64

class Message:
    def __init__(self, role=None, text=None, base64_image=None):
        self.role = role
        self.text = text
        self.base64_image = base64_image

    def add_prompt(self, role, prompt: str):
        self.role = role
        self.text = prompt

    def add_image(self, role, base64_image, prompt=None):
        self.base64_image = base64_image
        self.text = prompt
        self.role = role

    def get_dict(self):
        content = []
        if self.base64_image is not None:
            if self.text is not None:
                content.append(self.get_text_content(self.text))
            content.append(self.get_image_content(self.base64_image))
            message = {"role": self.role, "content": content}
            return message
        return {"role": self.role, "content": self.text}
    

    @staticmethod
    def encode_image(image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    @staticmethod
    def get_text_content(text):
        return {
            "type": "text",
            "text": text
        }

    @staticmethod
    def get_image_content(base64_image):
        image_type = 'image/jpeg'
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{image_type};base64,{base64_image}"
            }
        }


class History:
    def __init__(self, messages: list[Message]=None):
        if messages is None:
            messages = []
        self.messages = messages

    def add(self, message: Message):
        self.messages.append(message)

    def get_messages_json(self):
        return [message.get_dict() for message in self.messages]
    
def merge_histories(history1: History, history2: History):
    return History(history1.messages + history2.messages)