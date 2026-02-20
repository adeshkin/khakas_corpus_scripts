import random
import pandas as pd
import re
import pymorphy3
import unicodedata

pd.set_option('display.max_colwidth', None)

morph = pymorphy3.MorphAnalyzer(lang='ru')


def filter_words_by_ref_khakas(text, ref_text):
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


def filter_words_by_ref_non_khakas_latin(text, ref_text):
    ref_words = re.findall(r'\w+', ref_text.lower())

    if not ref_words:
        result = re.findall(r'\w+', text)
        return ' '.join(list(set(result)))

    pattern_string = '|'.join(re.escape(word) for word in ref_words)
    ref_pattern = re.compile(pattern_string)

    target_words = re.findall(r'\w+', text)

    result = []

    for word in target_words:
        if ref_pattern.search(word.lower()):
            if bool(re.search(r'[A-Za-z]', word)):
                result.append(word)

    return ' '.join(list(set(result)))


def get_lemma(word):
    parsed_word = morph.parse(word)[0]
    lemma = parsed_word.normal_form
    return lemma


def replace_words_skip_ref_text1(text, ref_text):
    # ref_words = set(re.findall(r'\w+', ref_text.lower()))
    # ref_words_lemma = [get_lemma(x) for x in ref_words]
    # ref_words_all = set(ref_words).union(set(ref_words_lemma))
    #
    # pattern_string = '|'.join(re.escape(word) for word in ref_words_all)
    # ref_pattern = re.compile(pattern_string)

    target_words = re.findall(r'\w+', text)

    old_new_dict = {'ӊ': 'ң', 'ӌ': 'ҷ',}
    for word in target_words:
        new_word_chars = []
        for char in word:
            new_word_chars.append(old_new_dict.get(char, char))
        new_word = "".join(new_word_chars)

        text = text.replace(word, new_word)
        # if new_word != word:
        #     print(word)
        #     print(new_word)
        #     print(text)
        #     print(ref_text)
        #     print()

    return text


def replace_words_skip_ref_text2(text, ref_text):
    # ref_words = set(re.findall(r'\w+', ref_text.lower()))
    # ref_words_lemma = [get_lemma(x) for x in ref_words]
    # ref_words_all = set(ref_words).union(set(ref_words_lemma))
    #
    # pattern_string = '|'.join(re.escape(word) for word in ref_words_all)
    # ref_pattern = re.compile(pattern_string)

    target_words = re.findall(r'\w+', text)

    old_new_dict = {
        'Ö': 'Ӧ',
        'ö': 'ӧ',
        'ÿ': 'ӱ',
    }

    for word in target_words:
        if word in ['Kövirág', 'Pöls', 'Schönherr']:
            new_word = word
        else:
            new_word_chars = []
            for char in word:
                new_word_chars.append(old_new_dict.get(char, char))
            new_word = "".join(new_word_chars)

        text = text.replace(word, new_word)
        if new_word != word:
            print(word)
            print(new_word)
            print(text)
            print(ref_text)
            print()

    return text


def replace_words_skip_ref_text3(text, ref_text):
    old_new_dict = {
        'ХХӀ': 'XXI',
        'ХӀ': 'XI',
        'Ӏ': 'I',
        'ӀКК': 'IKM',
        'ӀКМ': 'IKM',
        'ӀР': 'IP',
        'ӀӀ': 'II',
        'ӀӀӀ': 'III',
        'ӱчүн': 'ӱчӱн',
        'plorerнi': 'plorer-ні',
        'lspiceнi': 'lspice-ні',
        'WEPклӱстi': 'WEP-клӱсті',
        'DLLнi': 'DLL-ні',
        'BAdтi': 'BAdI-ні',
        'ARC_SD_VTTK_DELETEнi': 'ARC_SD_VTTK_DELETE-ні',
        'Jдірткен': 'Ӧдірткен',
        'чeс': 'чӱс',
        'Eлӱкӱн': 'Ӱлӱкӱн',
        'авиацияyаң': 'авиациянаң',
        'Правительствоныy': 'Правительствоның',
        'changeTypeполған': 'changeType полған',
        'PokerStarsСНГ': 'PokerStars СНГ',
        'xxxxxxномер': 'xxxxxx номер',
        'HTTPпанацея': 'HTTP панацея'
    }
    # # 'ІіҒғҢңҶҷӦӧӰӱ'
    for old, new in old_new_dict.items():
        text = text.replace(old, new)

    text = text.replace('Ӏ', 'І')

    return text


def replace_words_skip_ref_text4(text, ref_text):
    ref_words = set(re.findall(r'\w+', ref_text.lower()))
    ref_words_lemma = [get_lemma(x) for x in ref_words]
    ref_words_all = set(ref_words).union(set(ref_words_lemma))

    pattern_string = '|'.join(re.escape(word) for word in ref_words_all)
    ref_pattern = re.compile(pattern_string)

    target_words = re.findall(r'\w+', text)

    old_new_dict = {
        'Ö': 'Ӧ',
        'ö': 'ӧ',
        'ÿ': 'ӱ',
    }

    for word in target_words:
        if ref_pattern.search(word.lower()):
            new_word = word
        else:
            new_word_chars = []
            for char in word:
                new_word_chars.append(old_new_dict.get(char, char))
            new_word = "".join(new_word_chars)

        text = text.replace(word, new_word)
        if new_word != word:
            print(word)
            print(new_word)
            print(text)
            print(ref_text)
            print()

    return text


def replace_words_skip_ref_text_final(text):
    target_words = re.findall(r'\w+', text)
    old_new_dict1 = {'j': 'ӧ', 'y': 'ң', 'e': 'ӱ', 'b': 'і', 'u': 'ғ', 'x': 'ҷ'}

    old_new_dict = old_new_dict1.copy()
    for key, value in old_new_dict1.items():
        old_new_dict[key.upper()] = value.upper()

    for word in target_words:
        new_word = word
        # xX
        if bool(re.search(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]', word)) and bool(re.search(r'[jyebuxJYEBUX]', word)):
            new_word_chars = []
            for char in word:
                new_word_chars.append(old_new_dict.get(char, char))
            new_word = "".join(new_word_chars)

        text = text.replace(word, new_word)
        if new_word != word:
            print(word)
            print(new_word)
            print(text)
            print()

    return text


def find_words_with_symbol(text, symbol):
    words = re.findall(r'\b\w*' + re.escape(symbol) + r'\w*\b', text)
    # words = re.findall(r'.{0,30}' + re.escape(symbol) + r'.{0,30}', text)
    return sorted(set(words))


def find_new_roman_khak(text):
    # pattern = r'\b(?=[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱjubxye]*[jubxye])(?=[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱjubxye]*[а-яА-ЯёЁ])[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱjubxye]+\b'
    pattern = r'\b(?=[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱye]*[ye])(?=[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱye]*[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ])[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱye]+\b'

    matches = re.findall(pattern, text, flags=re.IGNORECASE)

    return len(matches) > 0


def find_by_letters(target_word, word_list):
    if not word_list:
        return None

    # Преобразуем искомое слово в множество уникальных букв
    target_set = set(target_word)

    # Функция max ищет слово, у которого пересечение множеств (&) имеет максимальную длину
    result = max(word_list, key=lambda w: len(target_set & set(w)))

    return result


def find_mixed_script_words(text, ru_text):
    found_words = []

    target_words = re.findall(r'\w+', text)
    ru_words = re.findall(r'\w+', ru_text)

    for word in target_words:
        latin_count = len(re.findall(r'[acekmopyxABCEHKMOPTXY]', word))
        cyrillic_count = len(re.findall(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]', word))

        if len(word) > 1:
            if latin_count > 0:
                if cyrillic_count >= latin_count:
                    found_words.append(word)

    result = []
    for found_word in found_words:
        r_word = find_by_letters(found_word, ru_words)
        result.append(f'{found_word}####{r_word}')

    return ' '.join(result)


def replace_words4(text, ru_text):
    with open('latin_error_cyrl_clean.txt') as f:
        lines = f.readlines()

    with open('latin_error_cyrl_clean2.txt') as f:
        lines.extend(f.readlines())

    old_new_map = {x.split("####")[0].strip(): x.split("####")[1].strip() for x in lines}
    for old, new in old_new_map.items():
        for new_char, old_char in zip('acekmopyxABCEHKMOPTXYiI', 'асекморухАВСЕНКМОРТХУіІ'):
            new = new.replace(old_char, new_char)

        text = text.replace(old, new)
        text = text.replace(old.lower(), new.lower())

    return text


def replace_words5(text):
    with open('latin_error_cyrl_clean.txt') as f:
        lines = f.readlines()

    with open('latin_error_cyrl_clean2.txt') as f:
        lines.extend(f.readlines())

    old_new_map = {x.split("####")[0].strip(): x.split("####")[1].strip() for x in lines}
    for old in old_new_map.values():
        new = old
        for new_char, old_char in zip('acekmopyxABCEHKMOPTXYiI', 'асекморухАВСЕНКМОРТХУіІ'):
            new = new.replace(old_char, new_char)

        text = text.replace(old, new)
        text = text.replace(old.lower(), new.lower())
        # if old != new:
        #     for symbol in old:
        #         print(symbol, unicodedata.name(symbol))
        #     print('-----')
        #     for symbol in new:
        #         print(symbol, unicodedata.name(symbol))
        #     print()
        #     print()

    return text


def replace_words6(text, old_new_map):
    old_text = text
    target_words = re.findall(r'\w+', text)

    for word in target_words:
        new_word = word
        for old, new in old_new_map.items():
            if new_word == old:
                new_word = new_word.replace(old, new)
            if new_word == old.capitalize():
                new_word = new_word.replace(old.capitalize(), new.capitalize())

        if new_word != word:
            print(word)
            print(new_word)
            print()
        text = text.replace(word, new_word)

    if text != old_text:
        print(old_text)
        print(text)
        print()
    return text


def replace_mixed_script_words(text, ru_text):
    found_words = []

    target_words = re.findall(r'\w+', text)
    #ru_words = re.findall(r'\w+', ru_text)
    text = text.replace('Іzеn', 'Изен')
    old_new_chars1 = {'i': 'і', 'a': 'а', 'e': 'е', 'c': 'с'}
    old_new_dict = old_new_chars1.copy()
    for key, value in old_new_chars1.items():
        old_new_dict[key.upper()] = value.upper()

    for word in target_words:
        latin_count = len(re.findall(r'[a-zA-Z]', word))
        cyrillic_count = len(re.findall(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]', word))

        if len(word) > 1:
            if cyrillic_count > 0 and latin_count > 0:
                new_word = word
                for old_char, new_char in old_new_dict.items():
                    new_word = new_word.replace(old_char, new_char)
                text = text.replace(word, new_word)

    return text


def prepare_defis_map():
    names = ['defis_words_custom.txt',
             'defis_words_dict_hrs_new34.txt']
    #'defis_words_uchebniki_docx.txt']
    data_dir = '/home/adeshkin/Desktop/defis_words'

    lines = []
    for name in names:
        path = f'{data_dir}/{name}'
        with open(path) as f:
            lines.extend(f.readlines())

    old_new_map = dict()
    for line in lines:
        line = line.strip()
        new = line
        old = line.replace('-', '')
        if old == new:
            print(old, new)
            continue
        old_new_map[old] = new

    return old_new_map


def get_dict_pairs():
    df_dict = pd.read_csv('/home/adeshkin/Desktop/defis_words/hrs_new34_clean_4_col.csv')
    df_dict['not_valid'] = df_dict.apply(lambda x: x['word'] == x['semgloss']
                                                   or len(x['word']) < 2
                                                   or len(x['semgloss']) < 2
                                                   or bool(re.search(r'[A-Za-z]', x['word']))
                                                   or bool(re.search(r'[A-Za-z]', x['semgloss'])), axis=1)
    df_dict['Источник'] = 'dict'
    pairs = df_dict[~df_dict['not_valid']][['semgloss', 'word', 'Источник']].values.tolist()

    return pairs


def main():
    df = pd.read_csv('../data/corpus_last_dance/corpus_100695_almost_final.csv')
    df['Хакасский1'] = df.apply(lambda x: replace_words_skip_ref_text1(x['Хакасский'], x['Русский']), axis=1)
    df['Хакасский2'] = df.apply(lambda x: replace_words_skip_ref_text2(x['Хакасский1'], x['Русский']), axis=1)
    df['Хакасский3'] = df.apply(lambda x: replace_words_skip_ref_text3(x['Хакасский2'], x['Русский']), axis=1)
    df['Хакасский4'] = df.apply(lambda x: replace_words4(x['Хакасский3'], x['Русский']), axis=1)
    df['Russian'] = df.apply(lambda x: replace_words5(x['Русский']), axis=1)
    df['Хакасский5'] = df.apply(lambda x: replace_words_skip_ref_text_final(x['Хакасский4']) if x[
                                                                                                    'Переводчик'] == 'Сагалакова Ольга Петровна' else
    x['Хакасский4'], axis=1)
    df['Хакасский6'] = df.apply(
        lambda x: replace_words6(x['Хакасский5'], prepare_defis_map()) if x['Источник'] == 'kjh_rus'
        else x['Хакасский5'], axis=1)

    # df['Хакасский6'] = df.apply(lambda x: replace_words6(x['Хакасский'], prepare_defis_map()) if x['Источник'] == 'kjh_rus'
    # else x['Хакасский'], axis=1)
    df['Khakas'] = df.apply(lambda x: replace_mixed_script_words(x['Хакасский6'], x['Russian']), axis=1)

    pairs = df[['Russian', 'Khakas', 'Источник']].values.tolist()
    pairs.extend(get_dict_pairs())
    ist_map = {'all': 'Англо-русский корпус Яндекса',
               'rus_kjh': 'Англо-русский корпус Яндекса',
               'prince': 'Художественное произведение',
               'kjh_rus': 'Учебники, статьи, пьесы',
               'dict': 'Хакасско-русский словарь'}

    df_new = pd.DataFrame(pairs, columns=['Русский', 'Хакасский', 'Источник'])
    df_new['Источник'] = df_new.apply(lambda x: ist_map.get(x['Источник'], x['Источник']), axis=1)
    df_sorted = df_new.sort_values(by='Русский', key=lambda x: x.str.len())
    df_sorted.to_csv('./corpus_last_sorted_russian.csv', index=False)
    df_sorted = df_new.sort_values(by='Хакасский', key=lambda x: x.str.len())
    df_sorted.to_csv('./corpus_last_sorted_khakas.csv', index=False)
    df_new.to_csv('./corpus_last.csv', index=False)


    # df['lat_cyrl_words'] = df.apply(lambda x: find_mixed_script_words(x['Хакасский4'], x['Русский']), axis=1)
    #
    text1 = ' '.join(df['lat_cyrl_words'].tolist())
    words1 = list(set(text1.split()))
    with open('./latin_error_cyrl.txt', 'w') as f:
        for word1 in words1:
            f.write(f'{word1}\n')

    print()
    print('lat_cyrl_words')
    print(len(words1))
    r_words = random.choices(words1, k=5)
    for r_word in r_words:
        print(r_word)
        for symbol in r_word:
            print(symbol, unicodedata.name(symbol))
        print()
        print()

    # print(repr(''.join(sorted(set(text)))))
    # print()
    # print('new_roman_khak')
    # print(df[df['new_roman_khak']][['Хакасский3', 'Русский']])

    # for symbol in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    #     words = find_words_with_symbol(text, symbol)
    #     if len(words) > 0:
    #         print(symbol)
    #         print(len(words))
    #         print(words[:10])
    #         print()


if __name__ == '__main__':
    main()

    # print(prepare_defis_map())

    # text1 = ' '.join(df_dict['word'].tolist())
    # text2 = ' '.join(df_dict['semgloss'].tolist())
    # text = text1 + text2
    # print(repr(''.join(sorted(set(text)))))

    # print('jyebux'.upper())
    # latin_pattern = re.compile(r'[acekmopyxABCEHKMOPTXY]')
    # word = 'комсомолецтерні' # чахайахтарын 11мВт/МГцке
    # has_latin = bool(latin_pattern.search(word))
    # print(has_latin)

    # Комплекстiң архитектура
    # Архитектурный облик комплекса

    # cyrillic_pattern = re.compile(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]')
    # cyrillic_count = len(re.findall(cyrillic_pattern, 'Blackjack'))
    # print(cyrillic_count)

    # EXБ####ЕХБ
