# pip install pyspellchecker
import re
from spellchecker import SpellChecker


def find_spelling_errors_with_context(texts_list, context_length=50):
    """
    Находит орфографические ошибки в списке русских текстов,
    извлекает контекст и предлагает исправления.

    Args:
        texts_list (list): Список строк для проверки.
        context_length (int): Количество символов контекста до и после слова.

    Returns:
        list: Список словарей с информацией об ошибках.
    """

    # Инициализируем проверку для русского языка
    try:
        spell = SpellChecker(language='ru')
    except Exception as e:
        print(f"Ошибка при загрузке словаря 'ru'. Убедитесь, что он установлен.")
        print("Попробуйте: pip install pyspellchecker")
        print(f"Ошибка: {e}")
        return []

    # Регулярное выражение для поиска слов на русском языке (включая дефисы)
    word_regex = re.compile(r'\b[а-яА-ЯёЁ-]+\b', re.IGNORECASE)

    all_errors = []

    for text in texts_list:
        # Находим все слова в тексте с их позициями
        for match in word_regex.finditer(text):
            word = match.group(0)

            # Проверяем, есть ли слово в словаре (приводим к нижнему регистру для проверки)
            if spell.unknown([word.lower()]):
                # 1. Находим исправление (самый вероятный кандидат)
                suggestion = spell.correction(word.lower())

                # 2. Находим всех кандидатов
                candidates = spell.candidates(word.lower())

                # 3. Сохраняем контекст
                start_index = match.start()
                end_index = match.end()

                # Контекст до слова
                context_before = text[max(0, start_index - context_length): start_index]

                # Контекст после слова
                context_after = text[end_index: min(len(text), end_index + context_length)]

                # Сохраняем результат
                error_info = {
                    "text": text,
                    "error_word": word,
                    "context_before": context_before,
                    "context_after": context_after,
                    "suggestion": suggestion,
                    "all_candidates": candidates
                }
                all_errors.append(error_info)

    return all_errors


# --- Пример использования ---

my_texts = [
    "Это первыц пример текста с явной ошбкой.",
    "Я люблю программирование и анализ данных на Питоне.",
    "Погода сегодня просто замечтельная, не правда ли?",
    "Мы купили малако и хлеб в магазине."
]

# data_dir = '/home/adeshkin/Desktop/defis_words'
# my_texts = []
# start = 10000
# with open(f'{data_dir}/uchebniki_docx_все_хак символы.txt') as f:
#     my_texts.append(f.read()[start:start+500])

# Находим ошибки
errors = find_spelling_errors_with_context(my_texts)

# Выводим результаты
if errors:
    print(f"Найдено ошибок: {len(errors)}\n")
    for error in errors:
        print("-" * 30)
        print(f"Слово с ошибкой: {error['error_word']}")
        print(f"Контекст:        ...{error['context_before']}[ {error['error_word']} ]{error['context_after']}...")
        print(f"Рекомендация:     {error['suggestion']}")
        print(f"Все варианты:     {error['all_candidates']}")
        print(f"В тексте:         {error['text']}")
        print("-" * 30 + "\n")
else:
    print("Ошибок не найдено.")
