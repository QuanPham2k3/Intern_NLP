import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# Tải các biến môi trường từ file .env
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)
# Định nghĩa các công cụ (tools) cho API GPT
tools = [
    {
        "type": "function",
        "function": {
            "name": "translate_to_english",
            "description": "Translate a sentence from Vietnamese to English.",
            "parameters": {
                "type": "object",
                "properties": {
                    "translatedSentence": {
                        "type": "string",
                        "description": "the English translated sentence from user's input."
                    }
                },
                "required": [
                    "translatedSentence"
                ]
            }
        }
    },
    {   
        "type": "function",
        "function": {
            "name": "extract_keywords",
            "description": "Extract health-related English keywords, no name, e.g: health, medical, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "description": "the related health keywords from user's input.",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["keywords"]
            },         
        },  
    }
]

def get_function_call(messages, gpt_model, tools=None, tool_choice=None):
    try:
        response = client.chat.completions.create(
            model=gpt_model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

# Hàm dịch văn bản từ tiếng Việt sang tiếng Anh
def translate_to_english(text):
    try:
        response = get_function_call(
            messages=[
                {"role": "system", "content": "You are a translator."},
                {"role": "user", "content": f'Translated into English: {text}'}
            ],
            gpt_model="gpt-4o-mini",
            tools=tools,
            tool_choice=None
        )
        translate = response.choices[0].message.tool_calls[0].function.arguments
        arguments = json.loads(translate)
        
        final = arguments.get('translatedSentence')
        
        return final
    except Exception as e:
        print(f"Error during translation: {e}")
        return None
    
# Hàm trích xuất từ khóa sức khỏe từ văn bản tiếng Anh
def extract_keywords(text):
    try:
        response = get_function_call(
            messages=[
                {"role": "system", "content": "You are a health expert"},
                {"role": "user", "content": f'Extract the health keyword from the following sentence: {text}'}
            ],
            gpt_model="gpt-4o-mini",
            tools=tools,
            tool_choice=None
        )
        keywords = response.choices[0].message.tool_calls[0].function.arguments
        arguments = json.loads(keywords)

        final = arguments.get('keywords')
        return final
    
    except Exception as e:
        print(f"Error during keyword extraction: {e}")
        return None

# Hàm xử lý từng entry trong file JSON
def process_entry(entry):
    try:
        if entry['response']['function'] == 'QA':

            translated_question = translate_to_english(entry['response']['question'])
            if translated_question:
                entry['response']['question'] = translated_question
                keywords = extract_keywords(translated_question)
                print(keywords)
                entry['response']['healthInformationKeywords'] = keywords
                entry['response']['language'] = 'en'

            for dialog in entry['dialog']:
                if '\nContext' in dialog['content']:
                    content_part, context_part = dialog['content'].split('\nContext', 1)
                    translated_content = translate_to_english(content_part.strip())
                    if translated_content:
                        dialog['content'] = f"{translated_content}\nContext{context_part.strip()}"
        return entry
    except Exception as e:
        print(f"Error processing entry: {e}")
        return entry

# Hàm xử lý file JSON với hỗ trợ Pooling và chỉ giới hạn số lượng mục
def process_responses(input_file, output_file):
    try:
        # Đọc dữ liệu từ file JSON
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        results = []
        # Xử lý từng mục (entry) tuần tự
        for entry in data:
            processed_entry = process_entry(entry)
            results.append(processed_entry)

        # Ghi kết quả đã xử lý vào file mới
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
        print(f"Processing completed. Output saved to {output_file}")
    
    except Exception as e:
        print(f"Error during processing responses: {e}")


# Khởi chạy chương trình chính
if __name__ == '__main__':
    input_file = 'test.json'
    output_file = 'processed_data.json'
    process_responses(input_file, output_file)



