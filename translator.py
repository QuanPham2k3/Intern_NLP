import json
import openai
from dotenv import load_dotenv
import os

# Tải các biến môi trường từ file .env
load_dotenv()

# Khởi tạo OpenAI API với API key
def init_openai_api():
    openai.api_key = os.getenv("OPENAI_API_KEY")

# Định nghĩa các công cụ (tools) cho API GPT-4
tools = [
    {
        "type": "function",
        "function": {
            "name": "translate_to_english",
            "description": "Dịch câu tiếng Việt sang tiếng Anh.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            },         
        },
    },
    {   
        "type": "function",
        "function": {
            "name": "extract_keywords",
            "description": "Trích xuất các từ khóa tiếng Anh liên quan sức khỏe, ví dụ: health.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            },         
        },  
    }
]

# Hàm dịch văn bản từ tiếng Việt sang tiếng Anh
def translate_to_english(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Dịch sang tiếng Anh: {text}"}],
            functions=tools,  # Đưa vào các tools (function definitions)
            function_call={"name": "translate_to_english"}
            
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error during translation: {e}")
        return None
    
# Hàm trích xuất từ khóa sức khỏe từ văn bản tiếng Anh
def extract_keywords(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Trích xuất từ khóa: {text}"}],
            functions=tools,  # Đưa vào các tools (function definitions)
            function_call={"name": "extract_keywords"}
            
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error during keyword extraction: {e}")
        return None

# Hàm xử lý từng entry trong file JSON
def process_entry(entry):
    try:
        if entry['response']['function'] == 'QA':
            print(entry['response']['question'])
            translated_question = translate_to_english(entry['response']['question'])
            print(translated_question)
            # if translated_question:
            #     entry['response']['question'] = translated_question
            #     keywords = extract_keywords(translated_question)
            #     entry['response']['healthInformationKeywords'] = keywords
            #     entry['response']['language'] = 'en'

            # for dialog in entry['dialog']:
            #     if '\nContext' in dialog['content']:
                    # content_part, context_part = dialog['content'].split('\nContext', 1)
                    #translated_content = translate_to_english(content_part.strip())
                    # if translated_content:
                    #     dialog['content'] = f"{translated_content}\nContext{context_part.strip()}"
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
    init_openai_api()
    input_file = 'test.json'
    output_file = 'processed_data.json'
    process_responses(input_file, output_file)
