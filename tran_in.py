import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import time

class BatchProcessor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.categorize_system_prompt = '''
        Translate the user's content into English, keep the "Context:" as it is. Extract relevant health-related keywords from the translated question and place them in the "healthInformationKeywords": []. 
        Update the [response][question] with the translated question, change the "language" field to "en", and return the result in the same JSON format. 
        The output must be in the same JSON format as the input, with only the translated content and extracted keywords changed.
        '''

    def extract_dialogs(self, data, input_num):
        '''
        - Chức năng: Lấy một số đoạn hội thoại từ dữ liệu gốc, tối đa bằng số lượng mà người dùng yêu cầu.
        - Dữ liệu vào: Dữ liệu JSON và số đoạn hội thoại cần lấy.
        - Dữ liệu ra: Danh sách các đoạn hội thoại đã trích xuất.
        '''
        extracted_dialogs = []  # Lưu các đoạn hội thoại đã trích xuất
        current_dialog_group = []   # Nhóm hiện tại các đoạn hội thoại có cùng câu đầu
        previous_dialog_start = None  
        dialog_count = 0  

        for entry in data:
            # Lấy câu đầu tiên của đoạn hội thoại hiện tại
            current_dialog_start = entry["dialog"][0]["content"]

            # Kiểm tra xem có phải đoạn mới hay không
            if current_dialog_start != previous_dialog_start:
                # Nếu nhóm trước có dữ liệu, lưu nó vào danh sách trích xuất
                if current_dialog_group:
                    extracted_dialogs.extend(current_dialog_group)
                    dialog_count += 1
                    current_dialog_group = [] # Reset nhóm hội thoại hiện tại

                # Nếu đã đủ đoạn hội thoại thì dừng
                if dialog_count >= input_num:
                    break

            # Thêm entry hiện tại vào nhóm hội thoại cùng câu đầu            
            current_dialog_group.append(entry)

            # Cập nhật câu đầu của đoạn hội thoại trước đó
            previous_dialog_start = current_dialog_start

        return extracted_dialogs

    def create_batch_file(self, data, batch_file):
        '''
            Chức năng: Tạo file batch gửi GPT từ dữ liệu trích xuất.
            Dữ liệu vào: Dữ liệu JSON trích xuất và tên file batch.
            Dữ liệu ra: File chứa các yêu cầu API để xử lý batch.
        '''
        try:
            with open(batch_file, 'w', encoding='utf-8') as file:
                # Chuẩn bị request cho chat completion
                for idx, entry in enumerate(data):
                    if entry['response']['function'] == 'QA':
                        custom_id = f"request-{idx + 1}"
                        text = json.dumps(entry, ensure_ascii=False)
                        body = {
                            "model": "gpt-4o-mini",
                            "response_format": {"type": "json_object"},
                            "messages": [
                                {"role": "system", "content": f"{self.categorize_system_prompt}"},
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

    def process_batch(self, input_file_path, endpoint, completion_window, data):
        '''
            Chức năng: Xử lý batch bằng cách upload file, gửi yêu cầu tới OpenAI API và kiểm tra trạng thái công việc batch cho đến khi hoàn tất.
            Dữ liệu vào: Đường dẫn file đầu vào, endpoint API, thời gian hoàn thành và dữ liệu gốc.
            Dữ liệu ra: Kết quả đã được xử lý hoặc lỗi.
        '''
        try:
            # Mở và tải file đầu vào jsonl để xử lý batch
            with open(input_file_path, "rb") as file:
                upload_file = self.client.files.create(
                    file=file,
                    purpose="batch"
                ) 

            # Tạo một batch job
            batch_job = self.client.batches.create(
                input_file_id=upload_file.id,
                endpoint=endpoint,
                completion_window=completion_window,
            )

            # Giám sát trạng thái của batch job
            while batch_job.status not in ["completed", "failed", 'cancelled']:
                batch_job = self.client.batches.retrieve(batch_job.id)
                print(f'Batch job status: {batch_job.status}... try again in 20 seconds')
                time.sleep(20) 

            if batch_job.status == "completed":
                result_file_id = batch_job.output_file_id # Lấy ID file kết quả
                result = self.client.files.content(result_file_id) # Lấy nội dung của file kết quả
                
                # Tách nội dung file JSONL thành các dòng
                result_lines = result.text.splitlines()

                # Tạo từ điển để lấy kết quả  theo custom_id
                Dict_batch = {}
                for line in result_lines:
                    result_data = json.loads(line)
                    cus_id = result_data['custom_id']
                    Dict_batch[cus_id] = result_data

                # Khởi tạo danh sách để lưu kết quả cuối cùng
                final = []

                # Lặp qua dữ liệu đầu vào và ánh xạ theo custom_id với kết quả tương ứng từ batch
                for idx, entry in enumerate(data):
                    custom_id = f"request-{idx + 1}"  
                    if custom_id in Dict_batch:
                        # Lấy message content từ batch data 
                        message_content = Dict_batch[custom_id]['response']['body']['choices'][0]['message']['content']
                        try:           
                            final.append(json.loads(message_content))
                        except json.JSONDecodeError:
                            final.append(message_content)
                    else:
                        # Nếu không có custom_id tương ứng trong batch_Data, thêm entry gốc
                        final.append(entry)

                # Ghi kết quả cuối cùng vào file "final_batch.json"
                with open('final_batch.json', 'w', encoding='utf-8') as file:
                    json.dump(final, file, ensure_ascii=False, indent=4)
                print("Batch job completed successfully, results saved in final_batch.json")         

            else:
                print(f'Batch job failed with status {batch_job.status}')
                return None

        except Exception as e:
            print(f"Lỗi trong quá trình xử lý batch: {e}")

    # Chạy toàn bộ quy trình từ đọc dữ liệu, trích xuất đoạn hội thoại, tạo file batch và xử lý batch.
    def run(self, input_file, input_num):
        try:
            # Đọc dữ liệu từ file JSON ban đầu
            with open(input_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Trích xuất các đoạn hội thoại theo input
            extracted_data = self.extract_dialogs(data, input_num)

            # Lưu dữ liệu đã trích xuất vào file JSON
            extracted_file = "extracted_data.json"
            with open(extracted_file, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=4)
            
            # Tạo file batch từ dữ liệu trích xuất
            batch_file = "batch_input.jsonl"
            self.create_batch_file(extracted_data, batch_file)

            endpoint = '/v1/chat/completions'
            completion_window = '24h'

            # Chạy batch từ file batch đã tạo
            self.process_batch(batch_file, endpoint, completion_window, extracted_data)

        except Exception as e:
            print(f"Lỗi khi đọc file đầu vào hoặc chạy batch: {e}")

if __name__ == '__main__':
    load_dotenv()
    API_KEY = os.getenv("OPENAI_API_KEY")
    processor = BatchProcessor(api_key=API_KEY)
    user_input = int(input("Nhập số đoạn hội thoại cần trích xuất: "))
    processor.run("sample_data.json", user_input)
