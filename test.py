import json
import openai
from dotenv import load_dotenv
import os

# Tải các biến môi trường từ file .env
load_dotenv()

# Khởi tạo OpenAI API với API key
def init_openai_api():
    openai.api_key = os.getenv("OPENAI_API_KEY")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["c", "f"]},
                },
                "required": ["location", "unit"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                },
                "required": ["symbol"],
                "additionalProperties": False,
            },
        },
    },
]

messages = [{"role": "user", "content": "What's the weather like in Boston today?"}]
completion = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    # highlight-start
    tool_choice="required"
    # highlight-end
)
init_openai_api()
print(completion)