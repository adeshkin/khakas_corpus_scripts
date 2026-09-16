import os
import pandas as pd

# 1. Укажите путь к вашему исходному файлу
input_file = "/home/adeshkin/khakas_projects/khakas_corpus_scripts/coregrammar_dataset/coregrammar_dataset/output/coregrammar_100000/sentences_100/sentences_001_kjh.csv"

# 2. Читаем исходный CSV-файл
df = pd.read_csv(input_file)

# 3. Создаем новую таблицу, выбирая и дублируя столбцы в нужном порядке
# Используем [['ru', 'kjh']] и копируем столбцы для нового порядка
new_df = pd.DataFrame(
    {
        "ru": df["ru"],
        "kjh": df["kjh"],
        "kjh_2": df["kjh"],  # В pandas названия столбцов должны быть уникальными,
        "ru_2": df["ru"],  # поэтому добавляем суффиксы (их можно переименовать)
    }
)

# Если вам нужно переименовать столбцы обратно в точные копии (ru, kjh, kjh, ru):
new_df.columns = ["ru", "kjh", "kjh", "ru"]
new_df = new_df.sample(frac=1, random_state=42).reset_index(drop=True)
# 4. Формируем новое имя файла (старое имя + '_модифицированный')
file_name, file_ext = os.path.splitext(input_file)
output_file = f"{file_name}_fix_col{file_ext}"

# 5. Сохраняем результат в новый CSV-файл
new_df.to_csv(output_file, index=False, encoding="utf-8")

print(f"Файл успешно сохранен как: {output_file}")
