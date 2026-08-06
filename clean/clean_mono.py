import os
from glob import glob
import re
import unicodedata
from razdel import sentenize

latin_pattern = re.compile(r'[a-zA-Z]')
cyrillic_pattern = re.compile(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]')


def count_unique_chars(word):
    latin_chars = set(latin_pattern.findall(word.lower()))
    cyrillic_chars = set(cyrillic_pattern.findall(word.lower()))

    return len(latin_chars), len(cyrillic_chars)


def analyze_words(sentences):
    latin_words = []
    mixed_words = []

    for sentence in sentences:
        words = re.findall(r'\b\w+\b', sentence)

        for word in words:
            lat_count, cyr_count = count_unique_chars(word)

            has_latin = lat_count > 0
            # has_latin = 'y' in word
            has_cyrillic = cyr_count > 0

            if has_latin and not has_cyrillic:
                latin_words.append(word)

            if has_latin and has_cyrillic:
                mixed_words.append(word)

    return list(set(latin_words)), list(set(mixed_words))


def find_lat_cyr_words(sents, print_latin=True):
    lat_words, lat_cyr_words = analyze_words(sents)
    if print_latin:
        print(f'Latin words = {len(lat_words)}')
        for word in lat_words:
            print(word)
            print()
        print(f'Latin words = {len(lat_cyr_words)}')
        print()

    print(f'Latin-cyrillic words = {len(lat_cyr_words)}')
    for word in lat_cyr_words:
        latin_chars = set(latin_pattern.findall(word))
        cyrillic_chars = set(cyrillic_pattern.findall(word))
        print(word)
        print(latin_chars)
        print(cyrillic_chars)
        print()
    print(f'Latin-cyrillic words = {len(lat_cyr_words)}')
    print()


def find_word_with_symbol(text, symbol):
    words = re.findall(r'\b\w*' + re.escape(symbol) + r'\w*\b', text)

    return sorted(set(words))


def find_context_with_symbol(text, symbol):
    examples = re.findall(r'.{0,15}' + re.escape(symbol) + r'.{0,15}', text)

    return sorted(set(examples))


def join_cyr():
    data_dir = '/home/adeshkin/Downloads/cyrillic'
    paths = sorted(glob(os.path.join(data_dir, '*.txt')))
    texts = []
    for path in paths:
        with open(path, 'r') as f:
            text = f.read()
        texts.append(text)
    all_text = '\n\n\n#####\n\n\n'.join(texts)
    with open('/home/adeshkin/Downloads/cyrillic.txt', 'w') as f:
        f.write(all_text)


def join_bel():
    data_dir = '/home/adeshkin/Downloads/beloglazov'
    paths = sorted(glob(os.path.join(data_dir, '*.txt')))
    texts = []
    for path in paths:
        with open(path, 'r') as f:
            text = f.read()
        texts.append(text)
    all_text = '\n\n\n#####\n\n\n'.join(texts)
    with open('/home/adeshkin/Downloads/beloglazov.txt', 'w') as f:
        f.write(all_text)


def join_mix():
    data_dir = '/home/adeshkin/Downloads/mixed'
    paths = sorted(glob(os.path.join(data_dir, '*.txt')))
    texts = []
    for path in paths:
        with open(path, 'r') as f:
            text = f.read()
        texts.append(text)
    all_text = '\n\n\n#####\n\n\n'.join(texts)
    with open('/home/adeshkin/Downloads/mixed.txt', 'w') as f:
        f.write(all_text)


def replace_lat_cyr_kjh(text):
    def replace_match(match):
        word = match.group(0)

        lat_count, cyr_count = count_unique_chars(word)

        if lat_count == 1 and 'i' in word and cyr_count > lat_count:
            word = word.replace('i', 'і')

        if lat_count == 1 and 'u' in word and cyr_count > lat_count:
            word = word.replace('u', 'ғ')

        if lat_count == 1 and 'j' in word and cyr_count > lat_count:
            word = word.replace('j', 'ӧ')

        if lat_count == 1 and 'I' in word and cyr_count > lat_count:
            word = word.replace('I', 'І')

        if lat_count == 1 and 'c' in word and cyr_count > lat_count:
            word = word.replace('c', 'с')

        if lat_count == 1 and 'C' in word and cyr_count > lat_count:
            word = word.replace('C', 'С')

        if lat_count == 1 and 'b' in word and cyr_count > lat_count:
            word = word.replace('b', 'і')

        if lat_count == 1 and 'p' in word and cyr_count > lat_count:
            word = word.replace('p', 'р')

        if lat_count == 1 and 'T' in word and cyr_count > lat_count:
            word = word.replace('T', 'Т')

        if lat_count == 1 and 'H' in word and cyr_count > lat_count:
            word = word.replace('H', 'Н')

        if lat_count == 2 and 'i' in word and cyr_count > lat_count:
            word = word.replace('i', 'і')

        if lat_count == 1 and 'e' in word and cyr_count > lat_count:
            word = word.replace('e', 'ӱ')

        if lat_count == 2 and 'e' in word and cyr_count > lat_count:
            word = word.replace('e', 'ӱ')

        if lat_count == 1 and 'y' in word and cyr_count > lat_count:
            word = word.replace('y', 'ң')

        if lat_count == 1 and 'x' in word and cyr_count > lat_count:
            word = word.replace('x', 'ҷ')

        if lat_count == 2 and 'x' in word and cyr_count > lat_count:
            word = word.replace('x', 'ҷ')

        if lat_count == 2 and 'j' in word and cyr_count > lat_count:
            word = word.replace('j', 'ӧ')

        if lat_count == 2 and 'u' in word and cyr_count > lat_count:
            word = word.replace('u', 'ғ')

        if lat_count == 2 and 'b' in word and cyr_count > lat_count:
            word = word.replace('b', 'і')

        if lat_count == 1 and 'E' in word and cyr_count > lat_count:
            word = word.replace('E', 'Ӱ')

        if lat_count == 3 and 'x' in word and cyr_count > lat_count:
            word = word.replace('x', 'ҷ')

        if lat_count == 1 and 'J' in word and cyr_count > lat_count:
            word = word.replace('J', 'Ӧ')

        if lat_count == 3 and 'j' in word and cyr_count > lat_count:
            word = word.replace('j', 'ӧ')

        if lat_count == 1 and 'K' in word and cyr_count > lat_count:
            word = word.replace('K', 'К')

        if lat_count == 1 and 'M' in word and cyr_count > lat_count:
            word = word.replace('M', 'М')

        return word

    # pattern = r'[a-zA-Zа-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]+'
    # {'j': 'ӧ', 'y': 'ң', 'e': 'ӱ', 'b': 'і', 'u': 'ғ', 'x': 'ҷ'}
    pattern = r'\w+'
    return re.sub(pattern, replace_match, text)


def replace_kjh(text):
    old_new_dict = {
        'ӌ': 'ҷ',
        'Ӌ': 'Ҷ',
        'Ӊ': 'Ң',
        'ӊ': 'ң',
        'ӀӀ': 'II',
        'Ӏ': 'І',
        'ӏ': 'І',
        '\ufeff': ' ',
        '\xad': '',

        'Ö': 'ӧ',
        'ö': 'ӧ',
        'ÿ': 'ӱ',
        'Ÿ': 'Ӱ',
        'ў': 'ӱ',
        'ӯ': 'ӱ',
        'Қ': 'К',
        'ҡ': 'к',
        'ҫ': 'с',

        'phrasӱos': 'phraseos',
        'nеos': 'neos',
        'ӱtңmon': 'etymon',
        'ХV': 'XV',
        'ҶVI': 'XVI',
        'IХ': 'IX',
        'calqғe': 'calque',
        'ӱғphӱmia': 'euphemia',
        'lӱҷikos': 'lexikos',
        'gеist': 'geist',
        'ХIV': 'XIV',
        'j': 'ӧ',
        'y': 'ң',
        'b': 'і',
        'e': 'ӱ',
        'u': 'ғ',
        'x': 'ҷ',
        'c': 'с',

        'J': 'Ӧ',
        'B': 'І',
        'I': 'І',
        'ХХI': 'XXI',
        'ХVII': 'XVII',
        'ХII': 'XII',
        'ХIХ': 'XIX',
        'ХIII': 'XIII',
        'i': 'і',

        'XVІІ': 'XVII',
        'Kӱpі': 'Кӱрі',
        'оp': 'ор',
        'ІV': 'IV',
        'arhaіos': 'archaios',

        'ӱtңmon': 'etymon',
        'сalqғӱ': 'calque',
        'Oҷ': 'Ох',
        'sңnonңmos': 'synonymos',
        'nӱos': 'neos',
        'phrasӱos': 'phraseos',
        'ІX': 'IX',
        'lӱҷіkos': 'lexikos',
        'onomastіkos': 'onomastikos',
        'phrasіs': 'phrasis',
        'VІІ': 'VII',
        'ХІX': 'XIX',

        'sӱmasіa': 'semasia',
        'XVІІІ': 'XVIII',
        'ӱtіmologіa': 'etimologia',
        'VІІІ': 'VIII',
        'lӱҷіs': 'lexis',
        'XІV': 'XIV',

        'сhaos': 'chaos',
        'phrasӱos': 'phraseos',
        'arсhaіos': 'archaios',

        'Kіp': 'Кір',

        'ааp': 'аар',
        'VІ': 'VI',
        'gӱіst': 'geist',
        'XVІ': 'XVI',

        'onңma': 'onyma',
        'antі': 'anti',
        'ӱғphӱmіa': 'euphemia',
        'ӱtңmon': 'etymon',
        'XVIIІ': 'XVIII',
        'ХIX': 'XIX',
        'ӱtңmon': 'etymon',

    }
    # pattern = r'[a-zA-Zа-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]+'
    old_new_dict = {
        'j': 'ӧ', 'y': 'ң', 'e': 'ӱ',
        'b': 'і', 'u': 'ғ', 'x': 'ҷ',
        'i': 'і', 'I': 'І', 'E': 'Ӱ',
        'J': 'Ӧ', 'U': 'Ғ', 'c': 'с',
        'B': 'І', 'Y': 'Ң', 'C': 'С',
        'a': 'а', 'o': 'о', 'F': 'Ғ',
        'ӌ': 'ҷ', 'ӊ': 'ң',
        'XVІІ': 'XVII', 'VІ': 'VI', 'VІІІ': 'VIII',
        'XІ': 'XI', 'ІV': 'IV', 'XІX': 'XIX',
        'ХVІІІ': 'XVIII', 'VІІ': 'VII', 'ХVІІ': 'XVII',
        'ІX': 'IX',
        '\xad': '',
        '\ufeff': ' ',

    }

    old_new_dict = {
        'Ö': 'Ӧ',
        'ö': 'ӧ',
        'ÿ': 'ӱ',
        'ӊ': 'ң',
        'p': 'ҷ',
        'ҳ': 'х',
        'Ӏ': 'І',
        '\ufeff': ' ',
        'i': 'і',
        'e': 'е',
        'I': 'І',
        'u': 'ғ',
        'j': 'ӧ',
        'y': 'ң',
        'x': 'ҷ',
        'ХVІІІ': 'XVIII',
        'p': 'р',
        'Сӧcп': 'Сӧсп',
        'XІX': 'XIX',
        'XVІІІ': 'XVIII',
        'ХVІІ': 'XVII',

    }
    # ІіҒғҢңҶҷӦӧӰӱ
    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def check_data():
    path = '/home/adeshkin/Downloads/beloglazov.txt'  # mixed beloglazov

    with open(path, 'r') as f:
        text = f.read()

    text = replace_kjh(text)
    # text = replace_lat_cyr_kjh(text)
    # text = replace_lat_cyr_kjh(text)
    # text = replace_lat_cyr_kjh(text)
    # text = replace_kjh(text)
    sents = [sent.text for sent in sentenize(text)]

    find_lat_cyr_words(sents, print_latin=False)

    with open('/home/adeshkin/khakas_projects/data/mono/bel.txt', 'w') as f:
        f.write(text)

    print(repr(''.join(sorted(set(text)))))
    print()

    assert 'ІіҒғҢңҷӦӧӰӱ' == 'ІіҒғҢңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in ['\ufeff']:
        # examples = find_word_with_symbol(text, symbol)
        examples = find_context_with_symbol(text, symbol)

        if len(examples) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(examples))
            # print(*examples, sep='\n')
            print(examples)
            print()


def replace_kjh_vasyutkino_ozero(text):
    old_new_dict = {
        '\ufeff': ' ',
        'u': 'ғ',
        'E': 'Ӱ',
        'I': 'І',
        'J': 'Ӧ',
        'i': 'і',
        'j': 'ӧ',
        'e': 'ӱ',
        'x': 'ҷ',
        'y': 'ң',

    }
    # ІіҒғҢңҶҷӦӧӰӱ
    # {'j': 'ӧ', 'y': 'ң', 'e': 'ӱ', 'b': 'і', 'u': 'ғ', 'x': 'ҷ'}
    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def replace_ru_vasyutkino_ozero(text):
    old_new_dict = {
        'B': 'В',
        'a': 'а',
        'c': 'с',
        'e': 'е',
        'o': 'о',
        'p': 'р',


    }
    # ІіҒғҢңҶҷӦӧӰӱ
    # {'j': 'ӧ', 'y': 'ң', 'e': 'ӱ', 'b': 'і', 'u': 'ғ', 'x': 'ҷ'}
    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text

from preprocess_text import preproc
def check_data_vasyutkino_ozero():
    path = '/home/adeshkin/khakas_projects/khakas-sent-emb/data/vasyutkino_ozero/kjh_text_2.txt'

    with open(path, 'r') as f:
        text = f.read()
    text = replace_kjh_vasyutkino_ozero(text)
    # text = replace_ru_vasyutkino_ozero(text)
    parts = []
    for part in text.split('\n'):
        part = preproc(part)
        if len(part) > 0:
            parts.append(part)

    with open('/home/adeshkin/khakas_projects/khakas-sent-emb/data/vasyutkino_ozero/kjh_fixed.txt', 'w') as f:
        for part in parts:
            f.write(part + '\n')

    # text = replace_kjh(text)
    # text = replace_lat_cyr_kjh(text)
    # text = replace_lat_cyr_kjh(text)
    # text = replace_lat_cyr_kjh(text)
    # text = replace_kjh(text)
    # sents = [sent.text for sent in sentenize(text)]
    #
    # find_lat_cyr_words(sents, print_latin=False)
    #
    # with open('/home/adeshkin/khakas_projects/data/mono/bel.txt', 'w') as f:
    #     f.write(text)

    print(repr(''.join(sorted(set(text)))))
    print()

    # assert 'ІіҒғҢңҷӦӧӰӱ' == 'ІіҒғҢңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ
    #
    # for symbol in 'Baceop':
    #     # examples = find_word_with_symbol(text, symbol)
    #     examples = find_context_with_symbol(text, symbol)
    #
    #     if len(examples) > 0:
    #         print(repr(symbol))
    #         print(unicodedata.name(symbol))
    #         print(len(examples))
    #         # print(*examples, sep='\n')
    #         print(examples)
    #         print()


if __name__ == "__main__":
    check_data_vasyutkino_ozero()
