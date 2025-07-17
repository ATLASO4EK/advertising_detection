from flask import Flask
from llm import QwenLLM
from config import QWEN_API_KEY

app = Flask(__name__)
model = QwenLLM(QWEN_API_KEY)