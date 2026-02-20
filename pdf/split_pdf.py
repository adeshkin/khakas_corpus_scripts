import os

from pypdf import PdfReader, PdfWriter


def split_pdf(input_file, split_at, save_dir):
    reader = PdfReader(input_file)
    total_pages = len(reader.pages)

    start_page = 0

    for i, end_page in enumerate(split_at):
        writer = PdfWriter()

        # В PDF страницы начинаются с 0, поэтому
        # если пользователь пишет "21", мы берем страницы от start_page до 21.
        # Цикл range(0, 21) возьмет индексы 0-20 (всего 21 страница).

        # Проверка, чтобы не выйти за границы файла
        actual_end = min(end_page, total_pages)

        for page_num in range(start_page, actual_end):
            writer.add_page(reader.pages[page_num])

        # Формируем имя файла
        output_filename = f"{save_dir}/part_{i + 1}_{start_page + 1}-{actual_end}.pdf"

        with open(output_filename, "wb") as output_pdf:
            writer.write(output_pdf)

        print(f"Создан файл: {output_filename} (страницы {start_page + 1} - {actual_end})")

        # Новая начальная страница — это конец предыдущего отрезка
        start_page = actual_end

    # (Опционально) Если остались страницы после последнего указанного индекса
    if start_page < total_pages:
        writer = PdfWriter()
        for page_num in range(start_page, total_pages):
            writer.add_page(reader.pages[page_num])

        output_filename = f"{save_dir}/part_remainder_{start_page + 1}-{total_pages}.pdf"
        with open(output_filename, "wb") as output_pdf:
            writer.write(output_pdf)
        print(f"Создан файл с остатком: {output_filename}")


# --- НАСТРОЙКИ ---
input_pdf_path = "/home/adeshkin/Desktop/словари/Толковый словарь хакасского языка том 1/Толковый словарь 1 ТОМ.pdf"  # Имя вашего исходного файла
pages_to_split = [21, 95, 173, 237, 305, 373, 423, 495, 523]  # Список конечных страниц
save_dir = "/home/adeshkin/Desktop/словари/Толковый словарь хакасского языка том 1/tolk_tom_1_splitted"
os.makedirs(save_dir, exist_ok=False)
split_pdf(input_pdf_path, pages_to_split, save_dir)