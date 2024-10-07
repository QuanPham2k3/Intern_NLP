import json

def extract_dialogs_in_batches(data, input_num):
    try:
        extracted_dialogs = []  # Lưu các đoạn hội thoại đã trích xuất
        previous_dialog_start = None  

        user_content_count = 0   

        for entry in data:
            # Lấy câu đầu tiên của đoạn hội thoại hiện tại
            current_dialog_start = entry["dialog"][0]["content"]

            # Nếu đoạn hội thoại hiện tại có câu đầu giống với đoạn trước
            if current_dialog_start == previous_dialog_start:
                # Nếu số lượng content của user trong nhóm <= 5, lưu nhóm hiện tại
                if user_content_count <= input_num :
                    extracted_dialogs.append(entry)
                # Reset nhóm và đếm số content của user
                user_content_count = 0

            # Nếu câu đầu khác
            if current_dialog_start != previous_dialog_start:
                if user_content_count <= input_num :
                    extracted_dialogs.append(entry)
                user_content_count = 0
                

            # Đếm số lượng câu content của user trong đoạn hội thoại hiện tại
            for dialog in entry["dialog"]:
                if dialog["role"] == "user":
                    user_content_count += 1

            # Cập nhật câu đầu tiên trước đó
            previous_dialog_start = current_dialog_start

        # Kiểm tra nếu nhóm cuối cùng thỏa mãn điều kiện thì lưu 
        if user_content_count <= input_num:
            extracted_dialogs.append(entry)

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
    input_num =  5
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
