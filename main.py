import re


def analyze_words(sentences):
    latin_pattern = re.compile(r'[a-zA-Z]')
    cyrillic_pattern = re.compile(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]')

    latin_only_words = []
    mixed_words = []

    for sentence in sentences:
        words = re.findall(r'\b\w+\b', sentence)

        for word in words:
            has_latin = bool(latin_pattern.search(word))
            has_cyrillic = bool(cyrillic_pattern.search(word))

            if has_latin and not has_cyrillic:
                latin_only_words.append(word)

            if has_latin and has_cyrillic:
                mixed_words.append(word)

    return list(set(latin_only_words)), list(set(mixed_words))


# Пример использования:
khakas_sentences = [
    "Хакас тілі — читіген чирінің тілі.",
    "Python программалоо тілі хакас тілінде де тузаланылча.",
    "Мынау word латиницада язылған.",
    "Смешанное слово: cто (первая буква 'c' — латинская).",  # Пример типичной ошибки
    "I (латинская i) - буква, похожая на хакасскую і."
]

latin_only, mixed = analyze_words(khakas_sentences)

print("1) Слова только на латинице:")
print(latin_only)

print("\n2) Смешанные слова (латиница + кириллица):")
print(mixed)
