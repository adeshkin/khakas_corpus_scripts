import re


def hyphenate_mixed_words(text):
    pattern = r'([A-Za-z]+)([А-Яа-яІіҒғҢңҶҷӦӧӰӱ]+)'

    replacement = r'\1-\2'

    return re.sub(pattern, replacement, text)


# # Тестовые данные
# text = 'ол windowsха хынча, androidтар даа бар. WhatsAppта чоохтасча.'
# result = hyphenate_mixed_words(text)
#
# print(f"До:    {text}")
# print(f"После: {result}")

import re


def fix_khakass_text(text):
    # Словарь замен согласно вашему условию
    old_new_dict = {
        'j': 'ӧ',
        'y': 'ң',
        'i': 'і',
        'e': 'ӱ',
        'b': 'і',
        'u': 'ғ',
        'x': 'ҷ'
    }

    # Функция, которая проверяет слово и делает замену
    def replace_match(match):
        word = match.group(0)

        # Проверяем, есть ли в слове хотя бы одна кириллическая буква
        # Диапазон а-я, А-Я, ё, Ё и специфические хакасские буквы, если они уже есть
        if re.search(r'[а-яА-ЯёЁӦӧҢңІіӰӱҒғҶҷ]', word):
            new_word_chars = []
            for char in word:
                # Заменяем символ, если он есть в словаре, иначе оставляем как есть
                new_word_chars.append(old_new_dict.get(char, char))
            return "".join(new_word_chars)

        # Если кириллицы нет, возвращаем слово без изменений
        return word

    # Регулярное выражение \w+ находит все слова (буквенно-цифровые последовательности)
    # Знаки препинания и пробелы останутся нетронутыми
    result = re.sub(r'\w+', replace_match, text)

    return result


# --- Пример использования ---

# Пример текста (смешанный: есть слова с кириллицей и без, и знаки препинания)
input_text = "Пyл text тестовый: сöjлӧ, кuнx, но слово english не меняем."

processed_text = fix_khakass_text(input_text)

print("Исходный текст:", input_text)
print("Результат:     ", processed_text)