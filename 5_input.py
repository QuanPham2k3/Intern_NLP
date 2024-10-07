import json

def extract_dialogs_in_batches(data, input_num):
    try:
        extracted_dialogs = []  # Lưu các đoạn hội thoại đã trích xuất
        previous_dialog_start = None  

        for entry in data:
            # Lấy câu đầu tiên của đoạn hội thoại hiện tại
            current_dialog_start = entry["dialog"][0]["content"]

            # Đếm số lượng câu content của user trong đoạn hội thoại hiện tại
            user_count = sum(1 for dialog in entry["dialog"] if dialog["role"] == "user")

            # Nếu câu đầu khác
            if current_dialog_start != previous_dialog_start:
                # Nếu số lượng câu của user trong nhóm <= input_num
                if user_count <= input_num:
                    extracted_dialogs.append(entry)  
                
            else:
                # Nếu câu đầu giống nhau, kiểm tra số lượng content của user
                if  user_count <= input_num:
                    extracted_dialogs.append(entry)  
            
            # Cập nhật câu đầu tiên trước đó
            previous_dialog_start = current_dialog_start


        return extracted_dialogs
    except Exception as e:
        print(f"Lỗi: {e}")
        return []

# Hàm lưu dữ liệu đã trích xuất vào file JSON
def save_extracted_data(extracted_data, output_filename):
    try:
        # Lưu kết quả vào file JSON
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)
        print(f"Đã trích xuất các đoạn hội thoại và lưu vào file {output_filename}")
    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu: {e}")

if __name__ == '__main__':
    input_file = "sample_data.json"
    output_filename = "new_data.json"
    input_num =  5  # Số lượng câu của user tối đa
    try:
        # Đọc dữ liệu từ file JSON
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Thực hiện trích xuất các đoạn hội thoại theo nhóm
        extracted_data = extract_dialogs_in_batches(data, input_num)

        # Lưu dữ liệu đã trích xuất vào file JSON
        save_extracted_data(extracted_data, output_filename)

    except Exception as e:
        print(f"Lỗi khi đọc file đầu vào: {e}")
