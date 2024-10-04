from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)


def process_batch(input_file_path, endpoint, completion_window, data):
    # Mở và tải file đầu vào lên để xử lý batch
    with open(input_file_path, "rb") as file:
        upload_file = client.files.create(
            file=file,
            purpose="batch"  # Đặt mục đích của file là "batch"
        ) 

    # Tạo một batch job với endpoint , thời gian
    batch_job = client.batches.create(
        input_file_id=upload_file.id,  # ID của file đã tải lên
        endpoint=endpoint,
        completion_window=completion_window,  
    )
    
    # Giám sát trạng thái của batch job, lặp cho đến khi hoàn thành, thất bại, hoặc bị hủy
    while batch_job.status not in ["completed", "failed", 'cancelled']:
        batch_job = client.batches.retrieve(batch_job.id)  # Lấy thông tin trạng thái mới nhất của batch      
        print(f'Batch job status: {batch_job.status}... try again in 20 seconds')
        time.sleep(20) 
    
    if batch_job.status == "completed":
        result_file_id = batch_job.output_file_id  # Lấy ID file kết quả
        result = client.files.content(result_file_id)  # Lấy nội dung của file kết quả
    
        # Tách nội dung file JSONL thành các dòng
        result_lines = result.text.splitlines()  
        
        # Tạo từ điển để lấy kết quả  theo custom_id
        Dict_batch = {}
        for line in result_lines:
            result_data = json.loads(line)
            cus_id = result_data['custom_id']  # Lấy custom_id
            Dict_batch[cus_id] = result_data  # Lưu kết quả tương ứng với custom_id

        # Khởi tạo danh sách để lưu kết quả cuối cùng
        final = []

        # Lặp qua dữ liệu đầu vào và ánh xạ với kết quả tương ứng từ batch
        for idx, entry in enumerate(data):
            custom_id = f"request-{idx + 1}"  
            if custom_id in Dict_batch:
                # Lấy message content từ batch data 
                message_content = Dict_batch[custom_id]['response']['body']['choices'][0]['message']['content']
                try:           
                    final.append(json.loads(message_content))
                except json.JSONDecodeError:
                    # Nếu không phải JSON, thêm message_content dưới dạng chuỗi
                    final.append(message_content)
            else:
                # Nếu không có custom_id tương ứng trong batch_Data, thêm entry gốc
                final.append(entry)

        # Ghi kết quả cuối cùng vào file JSON
        with open('final_batch.json', 'w', encoding='utf-8') as file:
            json.dump(final, file, ensure_ascii=False, indent=4)
        
        return "Batch job completed successfully"
    else:
        # Thông báo nếu batch job thất bại
        print(f'Batch job failed with status {batch_job.status}')
        return None

# Đọc dữ liệu từ file JSON đầu vào
with open('test.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Đường dẫn file đầu vào JSONL, endpoint và thời gian hoàn thành
input_file_path = 'batch_input.jsonl'
endpoint = '/v1/chat/completions'
completion_window = '24h'


results = process_batch(input_file_path, endpoint, completion_window, data)
print(results)
