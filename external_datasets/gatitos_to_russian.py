#      https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key=API-ключ&lang=en-ru&text=time
import requests
import time
import json
import pandas as pd
from tqdm import tqdm

# ВАШ API КЛЮЧ ОТ ЯНДЕКС.СЛОВАРЯ
API_KEY = ''
URL = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'

OUTPUT_FILE = 'gatitos_yandex_dict_result_error.json'  # Сохраняем в JSON, так как структура сложная


def get_full_data(word):
    """Отправляет запрос к API и возвращает полный JSON-ответ."""
    params = {
        'key': API_KEY,
        'lang': 'en-ru',
        'text': word
    }

    try:
        response = requests.get(URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()  # Возвращаем все данные как есть

    except Exception as e:
        print(f"Ошибка при обработке слова '{word}': {e}")
        return None


def main():
    # Читаем исходные слова
    df = pd.read_csv('smol_gatitos.csv')
    df.fillna('', inplace=True)
    words = df['en'].tolist()
    words = [x.strip() for x in words if len(x.strip()) > 0]

    print(f"Загружено слов: {len(words)}")

    # Словарь для хранения всех результатов
    all_results = {}

    for i, word in tqdm(enumerate(words, 1), total=len(words)):
        data = get_full_data(word)

        if data is not None:
            all_results[word] = data

            # Проверяем, есть ли словарные статьи внутри 'def'
            if not('def' in data and len(data['def']) > 0):
                print(f"{i}/{len(words)}: '{word}' -> В словаре нет перевода")
        else:
            # Если произошла ошибка сети и т.д.
            all_results[word] = {"error": "failed_to_fetch"}

        # Пауза 0.1 сек (10 запросов в секунду - безопасно для Яндекса)
        time.sleep(0.1)

        # Сохраняем весь собранный словарь в JSON-файл
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # ensure_ascii=False позволяет сохранить русские буквы читаемыми
        # indent=4 делает файл красивым и читабельным для человека
        json.dump(all_results, f, ensure_ascii=False, indent=4)

    print("Готово! Все данные сохранены в", OUTPUT_FILE)


if __name__ == "__main__":
    main()
