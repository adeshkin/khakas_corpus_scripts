import re
import json
import gzip
from collections import Counter
import sys

# --- НАСТРОЙКИ ---

# 1. Укажите путь к вашему текстовому файлу (корпусу)
#    (Или к списку файлов)
CORPUS_FILES = ['/home/adeshkin/Desktop/defis_words/uchebniki_docx_все_хак символы_defis_norm.txt']

# 2. Укажите имя для вашего файла словаря
DICTIONARY_FILE = '/home/adeshkin/Desktop/defis_words/my_custom_kjh_uchebniki.json.gz'


def clean_russian(word_frequency, filepath_exclude, filepath_include):
    """Clean an Russian word frequency list

    Args:
        word_frequency (Counter):
        filepath_exclude (str):
        filepath_include (str):
    """
    letters = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")

    # remove words with invalid characters
    invalid_chars = list()
    for key in word_frequency:
        kl = set(key)
        if kl.issubset(letters):
            continue
        invalid_chars.append(key)
    for misfit in invalid_chars:
        word_frequency.pop(misfit)

    # remove words without a vowel
    no_vowels = list()
    vowels = set("аеёиоуыэюя")
    for key in word_frequency:
        if vowels.isdisjoint(key):
            no_vowels.append(key)
    for misfit in no_vowels:
        word_frequency.pop(misfit)

    # remove ellipses
    ellipses = list()
    for key in word_frequency:
        if ".." in key:
            ellipses.append(key)
    for misfit in ellipses:
        word_frequency.pop(misfit)

    # leading or trailing doubles a, "a'", "zz", ending y's
    doubles = list()
    for key in word_frequency:
        if key.startswith("аа") and key not in ("аарон", "аарона", "аарону"):
            doubles.append(key)
        elif key.startswith("ээ") and key not in ("ээг"):
            doubles.append(key)
    for misfit in doubles:
        word_frequency.pop(misfit)

    # TODO: other possible fixes?

    # remove small numbers
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= MINIMUM_FREQUENCY:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    # remove flagged misspellings
    for line in load_include_exclude(filepath_exclude):
        if line in word_frequency:
            word_frequency.pop(line)

    # Add known missing words back in (ugh)
    for line in load_include_exclude(filepath_include):
        if line in word_frequency:
            print("{} is already found in the dictionary! Skipping!".format(line))
        else:
            word_frequency[line] = MINIMUM_FREQUENCY

    return word_frequency

# 3. РЕГУЛЯРНОЕ ВЫРАЖЕНИЕ ДЛЯ СЛОВ
#    Это самый важный шаг. Вам нужно указать, что считать "словом".
#    Например, r'\b[a-zа-яё-]+\b' найдет слова на русском/английском с дефисами.
#
#    !! ВАЖНО: Добавьте сюда все буквы вашего алфавита.
#    Например, если в вашем языке есть буквы 'ä', 'ö', 'i', 'ӌ',
#    выражение должно выглядеть так: r'\b[a-zа-яёäöiӌ-]+\b'
#
WORD_REGEX = r'\b[а-яёіғңҷӧӱ-]+\b' # <--- ИЗМЕНИТЕ ЭТО

# -----------------

print("Начинаем обработку корпуса...")
word_counts = Counter()

try:
    for corpus_file in CORPUS_FILES:
        print(f"Читаем файл: {corpus_file}")
        with open(corpus_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Находим все слова, приводим к нижнему регистру
                words = re.findall(WORD_REGEX, line.lower())
                word_counts.update(words)

    print(f"\nНайдено {len(word_counts)} уникальных слов.")
    print(f"Всего слов обработано: {sum(word_counts.values())}")

    # 4. Сохраняем в gzipped JSON, как любит pyspellchecker
    print(f"Сохраняем словарь в {DICTIONARY_FILE}...")
    with gzip.open(DICTIONARY_FILE, 'wt', encoding='utf-8') as f:
        json.dump(word_counts, f)

    print("\n✅ Готово! Файл словаря создан.")

except FileNotFoundError as e:
    print(f"\n❌ Ошибка: Файл не найден: {e.filename}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Произошла непредвиденная ошибка: {e}")
    sys.exit(1)