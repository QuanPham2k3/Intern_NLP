import json

def extract_dialogs_in_batches(data, input_num):
    try:
        extracted_dialogs = []  # Lưu các đoạn hội thoại đã trích xuất
        current_dialog_group = []  # Nhóm hiện tại các đoạn hội thoại có cùng câu đầu
        previous_dialog_start = None  # Câu đầu tiên của đoạn trước
        dialog_count = 0  # Đếm số lượng đoạn hội thoại đã lấy

        for entry in data:
            if entry["dialog"]:
                # Lấy câu đầu tiên của đoạn hội thoại hiện tại
                current_dialog_start = entry["dialog"][0]["content"]

                # Kiểm tra xem có phải đoạn mới hay không (câu đầu khác đoạn trước)
                if current_dialog_start != previous_dialog_start:
                    # Nếu nhóm trước có dữ liệu, lưu nó vào danh sách trích xuất
                    if current_dialog_group:
                        extracted_dialogs.extend(current_dialog_group)
                        dialog_count += 1  # Tăng số đoạn hội thoại đã lấy
                        current_dialog_group = []  # Reset nhóm hội thoại hiện tại

                    # Nếu đã đủ  đoạn hội thoại thì dừng
                    if dialog_count >= input_num:
                        break

                # Thêm entry hiện tại vào nhóm hội thoại cùng câu đầu
                current_dialog_group.append(entry)
                
                # Cập nhật câu đầu của đoạn hội thoại trước đó
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
