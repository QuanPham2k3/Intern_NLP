import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

categorize_system_prompt = '''
Translate the user's content into English, keep the "Context:" as it is. Extract relevant health-related keywords from the translated question and place them in the "healthInformationKeywords": []. Update the [response][question] with the translated question, change the "language" field to "en", and return the result in the same JSON format. 
The output must be in the same JSON format as the input, with only the translated content and extracted keywords changed.
'''

# Hàm tạo batch file từ dữ liệu đầu vào
def create_batch_file(data, batch_file, categorize_system_prompt):
    try:
        with open(batch_file, 'w', encoding='utf-8' ) as file: # , '
            for idx, entry in enumerate(data):
                if entry['response']['function'] == 'QA':
                    # Chuẩn bị request cho chat completion
                    custom_id = f"request-{idx + 1}"
                    text = json.dumps(entry, ensure_ascii=False),
                    body = {
                        "model": "gpt-4o-mini",
                        "response_format": { 
                            "type": "json_object"
                        },
                        "messages": [
                            {"role": "system", "content": f"{categorize_system_prompt}"},
                            {"role": "user", "content": f"{text}"}
                        ],
                        "max_tokens": 1000
                    }

                    # Ghi từng request vào file batch
                    request_line = json.dumps({
                        "custom_id": custom_id,
                        "method": "POST",
                        "url": "/v1/chat/completions",
                        "body": body
                    }, ensure_ascii=False)

                    file.write(request_line + '\n')

        print(f"Batch file created successfully at {batch_file}")
    except Exception as e:
        print(f"Error creating batch file: {e}")

# Ví dụ đọc file input JSON chứa dữ liệu đầu vào
input_file = 'test.json'
output_batch_file = 'batch_input.jsonl'

try:
    # Đọc dữ liệu từ file JSON
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Tạo batch file từ dữ liệu đầu vào
    create_batch_file(data, output_batch_file, categorize_system_prompt)

except Exception as e:
    print(f"Error loading input file: {e}")

