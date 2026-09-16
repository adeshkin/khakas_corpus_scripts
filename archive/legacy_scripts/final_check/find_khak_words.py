import re


def filter_words_by_ref(text, ref_text):
    """
    Убирает слова из text, если они содержат внутри себя слова из ref_text.
    """

    # 1. Извлекаем слова из ref_text (используем нижний регистр для поиска)
    # \w+ находит последовательности букв, цифр и подчеркивания
    ref_words = re.findall(r'\w+', ref_text.lower())

    # Если в ref_text нет слов, возвращаем все слова из text как есть
    if not ref_words:
        return re.findall(r'\w+', text)

    # 2. Создаем регулярное выражение-паттерн из всех слов ref_text
    # re.escape нужен, чтобы экранировать спецсимволы, если они попадутся
    # '|'.join объединяет слова через ИЛИ
    pattern_string = '|'.join(re.escape(word) for word in ref_words)
    ref_pattern = re.compile(pattern_string)

    # 3. Извлекаем слова из основного текста (сохраняя исходный регистр для результата)
    target_words = re.findall(r'\w+', text)

    result = []

    for word in target_words:
        # Проверяем: если паттерн находит совпадение ВНУТРИ слова (search)
        if ref_pattern.search(word.lower()):
            continue  # Пропускаем это слово (убираем его)

        result.append(word)

    return result


# --- Пример использования ---

main_text = "Банка стоит на столе. Банан желтый. Кот играет с клубком. Столешница дубовая."
reference = "бан стол"

# Логика:
# "бан" содержится в "Банка" и "Банан" -> они должны уйти.
# "стол" содержится в "столе" и "Столешница" -> они должны уйти.
# Остаться должны только слова про кота.

filtered_list = filter_words_by_ref(main_text, reference)

print("Исходный текст:", main_text)
print("Слова фильтра:", reference)
print("-" * 20)
print("Результат:", filtered_list)