import pandas as pd
import re

pd.set_option('display.max_colwidth', None)


def main1():
    df = pd.read_csv('../data/corpus_last_dance/corpus_100695_almost_final.csv')
    df_sorted = df.sort_values(by='Русский', key=lambda x: x.str.len())
    print(len(df_sorted))
    df_sorted.to_csv('../data/corpus_last_dance/corpus_100695_almost_final_sorted.csv', index=False)


def replace_symbols(text, ru_text):
    # # 'ІіҒғҢңҶҷӦӧӰӱ'
    old_new_dict = {'j': 'ӧ', 'y': 'ң', 'i': 'і', 'e': 'ӱ', 'b': 'і', 'u': 'ғ', 'x': 'ҷ'}
    full_dict = old_new_dict.copy()
    for key, value in old_new_dict.items():
        full_dict[key.upper()] = value.upper()

    homoglyphs = str.maketrans({
        'а': 'a', 'А': 'A',
        'с': 'c', 'С': 'C',
        'е': 'e', 'Е': 'E',
        'о': 'o', 'О': 'O',
        'р': 'p', 'Р': 'P',
        'х': 'x', 'Х': 'X',
        'і': 'i', 'І': 'I',
        # Можно добавить другие похожие пары, если нужно
    })

    russian_words_original = set(re.findall(r'\w+', ru_text.lower()))
    russian_words_normalized = {w.translate(homoglyphs) for w in russian_words_original}

    # Функция для обработки каждого найденного слова
    def process_word_match(match):
        word = match.group(0)
        word_lower = word.lower()

        has_cyrillic = bool(re.search(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]', word))

        # Нормализуем текущее слово для проверки
        word_norm = word_lower.translate(homoglyphs)

        # 1. Проверка: Есть ли слово в русском тексте (в оригинале или в нормализованном виде)?
        is_in_russian = (word_lower in russian_words_original) or \
                        (word_norm in russian_words_normalized)

        # Логика: Если есть кириллица И слова НЕТ в русском тексте -> меняем буквы
        # if has_cyrillic and not is_in_russian:
        if not is_in_russian and bool(re.search(r'[a-zA-Z]', word)):
            new_word_chars = []
            for char in word:
                # Если буква есть в словаре замен, меняем, иначе оставляем как есть
                new_word_chars.append(old_new_dict.get(char, char))
            print('before', word)
            print('after', "".join(new_word_chars))
            print()
            return "".join(new_word_chars)

        # Иначе возвращаем слово без изменений
        return word

    result_text = re.sub(r'\w+', process_word_match, text)

    return result_text


def replace_symbols_all(text, ru_text):
    # # 'ІіҒғҢңҶҷӦӧӰӱ'
    old_new_dict = {'i': 'і', 'Ö': 'Ӧ', 'ö': 'ӧ', 'ÿ': 'ӱ', 'ӌ': 'ҷ', 'ӊ': 'ң', 'Ӏ': 'І'}
    full_dict = old_new_dict.copy()
    for key, value in old_new_dict.items():
        full_dict[key.upper()] = value.upper()

    # homoglyphs = str.maketrans({
    #     'а': 'a', 'А': 'A',
    #     'с': 'c', 'С': 'C',
    #     'е': 'e', 'Е': 'E',
    #     'о': 'o', 'О': 'O',
    #     'р': 'p', 'Р': 'P',
    #     'х': 'x', 'Х': 'X',
    #     'і': 'i', 'І': 'I',
    #     # Можно добавить другие похожие пары, если нужно
    # })

    russian_words_original = set(re.findall(r'\w+', ru_text.lower()))
    #russian_words_normalized = {w.translate(homoglyphs) for w in russian_words_original}

    # Функция для обработки каждого найденного слова
    def process_word_match(match):
        word = match.group(0)
        word_lower = word.lower()

        has_cyrillic = bool(re.search(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]', word))

        # Нормализуем текущее слово для проверки
        #word_norm = word_lower.translate(homoglyphs)

        # 1. Проверка: Есть ли слово в русском тексте (в оригинале или в нормализованном виде)?
        # is_in_russian = (word_lower in russian_words_original) or \
        #                 (word_norm in russian_words_normalized)
        is_in_russian = word_lower in russian_words_original
        # Логика: Если есть кириллица И слова НЕТ в русском тексте -> меняем буквы
        # if has_cyrillic and not is_in_russian:
        if not is_in_russian:
            new_word_chars = []
            for char in word:
                # Если буква есть в словаре замен, меняем, иначе оставляем как есть
                new_word_chars.append(old_new_dict.get(char, char))

            return "".join(new_word_chars)

        # Иначе возвращаем слово без изменений
        return word

    result_text = re.sub(r'\w+', process_word_match, text)

    return result_text


def main1():
    df = pd.read_csv('../data/corpus_last_dance/corpus_100695_almost_final.csv')

    df['Хакасский'] = df.apply(
        lambda x: replace_symbols(x['Хакасский'], x['Русский']) if x['Переводчик'] == "Сагалакова Ольга Петровна" else
        x['Хакасский'], axis=1)

    df.to_csv('../data/corpus_last_dance/corpus_100695_almost_final_fix_sagal.csv')


def main():
    df = pd.read_csv('../data/corpus_last_dance/corpus_100695_almost_final_fix_sagal.csv')
    df['Хакасский'] = df.apply(lambda x: replace_symbols_all(x['Хакасский'], x['Русский']), axis=1)
    # text = ' '.join(df['Хакасский'].tolist())
    # print(repr(''.join(sorted(set(text)))))
    ist_map = {'all': 'Англо-русский корпус Яндекса',
               'rus_kjh': 'Англо-русский корпус Яндекса',
               'prince': 'Художественное произведение',
               'kjh_rus': 'Учебники, статьи, пьесы'}
    df['Источник'] = df.apply(lambda x: ist_map.get(x['Источник'], x['Источник']), axis=1)

    print(len(df))
    print(df['Источник'].value_counts())
    df1 = df[['Хакасский', 'Русский', 'Источник']]
    df1.to_csv('../data/corpus_last_dance/khakas_russian_parallel_corpus_100695_v1.csv')


if __name__ == '__main__':
    main()
