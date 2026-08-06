import pandas as pd
import re
from datasketch import MinHash, MinHashLSH
from tqdm import tqdm
import random

pd.set_option('display.max_rows', None)  # Показывать все строки
pd.set_option('display.max_columns', None)  # Показывать все столбцы
pd.set_option('display.width', None)  # Отключаем ограничение ширины экрана
pd.set_option('display.expand_frame_repr', False)  # Запрещаем перенос больших таблиц на следующую строку

# Настройки похожести
# 0.8 означает, что тексты должны совпадать на 80% (коэффициент Жаккара)
# Если нужно удалять только почти полные копии, поставьте 0.95
THRESHOLD = 0.85
NUM_PERM = 128  # Количество перестановок. 128 - баланс скорости и точности


def normalize_text(text):
    """
    Разбиваем текст на токены (слова).
    """
    if not isinstance(text, str):
        return []
    return re.findall(r'\w+', text.lower())


def get_minhash(tokens, num_perm):
    """
    Генерация MinHash подписи.
    """
    m = MinHash(num_perm=num_perm)
    for token in tokens:
        m.update(token.encode('utf8'))
    return m


def find_fuzzy_duplicates_and_show_examples(series, column_name):
    """
    Ищет нечеткие дубликаты и выводит примеры найденного.
    """
    print(f"\nОбработка столбца: '{column_name}'...")

    # Инициализация LSH
    lsh = MinHashLSH(threshold=THRESHOLD, num_perm=NUM_PERM)

    duplicates_indices = set()
    found_pairs = []  # Сюда будем складывать пары (Оригинал, Дубликат)

    # Используем tqdm для прогресс-бара
    for idx, text in tqdm(series.items(), total=len(series)):

        tokens = normalize_text(text)

        # Пропускаем слишком короткие строки (менее 2 слов),
        # их лучше обрабатывать точным совпадением, иначе MinHash может ошибаться
        if len(tokens) < 2:
            continue

        m = get_minhash(tokens, NUM_PERM)

        # Спрашиваем у индекса, есть ли похожее
        result = lsh.query(m)

        if result:
            # Нашли похожее!
            duplicates_indices.add(idx)

            # Сохраняем пример для отчета
            # result[0] - это индекс "Оригинала", который уже лежит в базе
            original_idx = result[0]
            original_text = series.loc[original_idx]

            # Добавляем пару в список (Оригинал, Текущий дубликат)
            found_pairs.append((original_text, text))
        else:
            # Не нашли, добавляем текущую строку как "Оригинал"
            lsh.insert(idx, m)

    print(f"Всего кандидатов на удаление в '{column_name}': {len(duplicates_indices)}")

    # --- ВЫВОД 5 СЛУЧАЙНЫХ ПРИМЕРОВ ---
    if found_pairs:
        print(f"\n--- Примеры того, что будет удалено ({column_name}) ---")
        # Берем 5 случайных или все, если их меньше 5
        count_to_show = min(10, len(found_pairs))
        samples = random.sample(found_pairs, count_to_show)

        for i, (orig, dup) in enumerate(samples, 1):
            print(f"Пара #{i}")
            print(f"   ОСТАВЛЯЕМ: {orig}")
            print(f"   УДАЛЯЕМ:   {dup}")
            print("-" * 30)
    else:
        print("Дубликатов не найдено.")

    return duplicates_indices


def main():
    path = '../data/kv1_done.csv'
    df = pd.read_csv(path)
    df['Файл'] = 'kv1_done'
    examples = df[['Хакасский', 'Русский', 'Источник', 'Файл']].values.tolist()

    path = '../data/ec_done.csv'
    df = pd.read_csv(path)
    df['Файл'] = 'ec_done'
    examples.extend(df[['Хакасский', 'Русский', 'Источник', 'Файл']].values.tolist())

    path = '../data/vl_done.csv'
    df = pd.read_csv(path)
    df['Источник'] = 'vl'
    df['Файл'] = 'vl_done'
    examples.extend(df[['Хакасский', 'Русский', 'Источник', 'Файл']].values.tolist())

    path = '../data/klr_done.csv'
    df = pd.read_csv(path)
    df['Файл'] = 'klr_done'
    examples.extend(df[['Хакасский', 'Русский', 'Источник', 'Файл']].values.tolist())

    path = '../data/til_done.csv'
    df = pd.read_csv(path)
    df['Источник'] = 'til'
    df['Файл'] = 'til_done'

    # remove artifacts `91;` `93;` of scraping
    df['Русский'] = df['Русский'].apply(lambda x: x.replace('91;', ' ').replace('93;', ' '))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: x.replace('91;', ' ').replace('93;', ' '))

    examples.extend(df[['Хакасский', 'Русский', 'Источник', 'Файл']].values.tolist())

    df = pd.DataFrame(examples, columns=['Хакасский', 'Русский', 'Источник', 'Файл'])

    print()
    print('len =', len(df))
    print('len(kv1_done) =', len(df[df['Файл'] == 'kv1_done']))
    print('len(ec_done) =', len(df[df['Файл'] == 'ec_done']))
    print('len(vl_done) =', len(df[df['Файл'] == 'vl_done']))
    print('len(klr_done) =', len(df[df['Файл'] == 'klr_done']))
    print('len(til_done) =', len(df[df['Файл'] == 'til_done']))
    print()

    df['kjh_lower'] = df['Хакасский'].str.lower()
    df['ru_lower'] = df['Русский'].str.lower()

    def clean_text(text):
        text = ' '.join(re.findall(r'[^\W\d_]+', text))
        text = re.sub(r'\\s+', ' ', text)

        return text.strip()

    df['kjh_word'] = df['kjh_lower'].apply(clean_text)
    df['ru_word'] = df['ru_lower'].apply(clean_text)

    df = df.drop_duplicates(subset='kjh_word', keep='first')
    print(len(df))

    df = df.drop_duplicates(subset='ru_word', keep='first')
    print(len(df))

    df = df.drop(df[df['kjh_word'] == df['ru_word']].index)
    print(len(df))

    print()
    print('len =', len(df))
    print('len(kv1_done) =', len(df[df['Файл'] == 'kv1_done']))
    print('len(ec_done) =', len(df[df['Файл'] == 'ec_done']))
    print('len(vl_done) =', len(df[df['Файл'] == 'vl_done']))
    print('len(klr_done) =', len(df[df['Файл'] == 'klr_done']))
    print('len(til_done) =', len(df[df['Файл'] == 'til_done']))
    print()

    df = df.reset_index(drop=True)

    dupes_khakas = find_fuzzy_duplicates_and_show_examples(df['kjh_word'], 'Хакасский')
    dupes_russian = find_fuzzy_duplicates_and_show_examples(df['ru_word'], 'Русский')

    all_dupes = dupes_khakas.union(dupes_russian)
    df = df.drop(index=list(all_dupes))

    print(f"\n==========================================")
    print(f"Итого удалено нечетких дубликатов: {len(all_dupes)}")
    print(f"Финальное количество строк: {len(df)}")

    print()
    print('len =', len(df))
    print('len(kv1_done) =', len(df[df['Файл'] == 'kv1_done']))
    print('len(ec_done) =', len(df[df['Файл'] == 'ec_done']))
    print('len(vl_done) =', len(df[df['Файл'] == 'vl_done']))
    print('len(klr_done) =', len(df[df['Файл'] == 'klr_done']))
    print('len(til_done) =', len(df[df['Файл'] == 'til_done']))
    print()

    df = df.reset_index(drop=True)

    dupes_khakas = find_fuzzy_duplicates_and_show_examples(df['Хакасский'], 'Хакасский')
    dupes_russian = find_fuzzy_duplicates_and_show_examples(df['Русский'], 'Русский')

    # Объединяем индексы на удаление
    all_dupes = dupes_khakas.union(dupes_russian)

    # Удаляем
    df = df.drop(index=list(all_dupes))

    print(f"\n==========================================")
    print(f"Итого удалено нечетких дубликатов: {len(all_dupes)}")
    print(f"Финальное количество строк: {len(df)}")

    print()
    print('len =', len(df))
    print('len(kv1_done) =', len(df[df['Файл'] == 'kv1_done']))
    print('len(ec_done) =', len(df[df['Файл'] == 'ec_done']))
    print('len(vl_done) =', len(df[df['Файл'] == 'vl_done']))
    print('len(klr_done) =', len(df[df['Файл'] == 'klr_done']))
    print('len(til_done) =', len(df[df['Файл'] == 'til_done']))
    print()

    df.to_csv('../data/kjh_ru_dedup.csv', index=False)


def main_mono():
    path = '../data/kjh_ru_dedup.csv'
    df = pd.read_csv(path)
    df['Файл'] = 'kjh_ru_dedup'
    examples = df[['Хакасский', 'Источник', 'Файл']].values.tolist()

    path = '../data/mono_done.csv'
    df = pd.read_csv(path)
    df['Файл'] = 'mono_done'
    examples.extend(df[['Хакасский', 'Источник', 'Файл']].values.tolist())

    df = pd.DataFrame(examples, columns=['Хакасский', 'Источник', 'Файл'])

    print()
    print('len =', len(df))
    print(df['Файл'].value_counts())
    print()

    df['kjh_lower'] = df['Хакасский'].str.lower()

    def clean_text(text):
        text = ' '.join(re.findall(r'[^\W\d_]+', text))
        text = re.sub(r'\\s+', ' ', text)

        return text.strip()

    df['kjh_word'] = df['kjh_lower'].apply(clean_text)

    df = df.drop_duplicates(subset='kjh_word', keep='first')
    print(len(df))

    print()
    print('len =', len(df))
    print(df['Файл'].value_counts())
    print()

    df = df.reset_index(drop=True)

    dupes_khakas = find_fuzzy_duplicates_and_show_examples(df['kjh_word'], 'Хакасский')

    all_dupes = dupes_khakas
    df = df.drop(index=list(all_dupes))

    print(f"\n==========================================")
    print(f"Итого удалено нечетких дубликатов: {len(all_dupes)}")
    print(f"Финальное количество строк: {len(df)}")

    print()
    print('len =', len(df))
    print(df['Файл'].value_counts())
    print()

    df = df.reset_index(drop=True)

    dupes_khakas = find_fuzzy_duplicates_and_show_examples(df['Хакасский'], 'Хакасский')

    all_dupes = dupes_khakas
    df = df.drop(index=list(all_dupes))

    print(f"\n==========================================")
    print(f"Итого удалено нечетких дубликатов: {len(all_dupes)}")
    print(f"Финальное количество строк: {len(df)}")

    print()
    print('len =', len(df))
    print(df['Файл'].value_counts())
    print()

    df = df[df['Файл'] == 'mono_done']
    print()
    print('len =', len(df))
    print(df['Файл'].value_counts())
    print()

    df.to_csv('../data/mono_kjh_dedup.csv', index=False)


if __name__ == '__main__':
    main_mono()
