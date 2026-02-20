from pypdf import PdfReader, PdfWriter
import os

def split_pdf(input_path, save_dir, name):
    with open(input_path, 'rb') as file:
        reader = PdfReader(file)

        # Получаем общее количество страниц
        total_pages = len(reader.pages)

        # Определяем число частей
        num_parts = (total_pages + 4) // 5  # округляем вверх

        for i in range(num_parts):
            writer = PdfWriter()

            start_page = max(i * 5 - 1, 0)
            end_page = min((i + 1) * 5, total_pages)

            # Добавляем страницы к новому файлу
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            # Сохраняем файл
            idx = f'{i+1:03d}'
            folder = f'{save_dir}/{name}/{name}_{idx}'
            os.makedirs(folder, exist_ok=False)
            filename = f"{folder}/{name}_{idx}.pdf"

            with open(filename, 'wb') as out_file:
                writer.write(out_file)

if __name__ == "__main__":
    path = '/home/adeshkin/Desktop/словари/Толковый словарь хакасского языка том 1/tolk_tom_1_splitted/part_9_496-523.pdf'
    name = path.split('/')[-1].split('.')[0]
    save_dir = '/home/adeshkin/Desktop/tolk_tom_1'
    split_pdf(path, save_dir, name)
