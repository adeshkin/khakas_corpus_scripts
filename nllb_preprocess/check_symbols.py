import pandas as pd
import re
import unicodedata

latin_pattern = re.compile(r'[a-zA-Z]')
cyrillic_pattern = re.compile(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]')


def count_unique_chars(word):
    latin_chars = set(latin_pattern.findall(word))
    cyrillic_chars = set(cyrillic_pattern.findall(word))

    return len(latin_chars), len(cyrillic_chars)


def analyze_words(sentences):
    latin_words = []
    mixed_words = []

    for sent in sentences:
        words = re.findall(r'\b\w+\b', sent)

        for word in words:
            lat_count, cyr_count = count_unique_chars(word)

            has_latin = lat_count > 0
            has_cyrillic = cyr_count > 0

            if has_latin and not has_cyrillic:
                latin_words.append(word)

            if has_latin and has_cyrillic:
                mixed_words.append(word)

    print('len mixed_words:', len(mixed_words))

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
    pattern = r'\b\w*' + re.escape(symbol) + r'\w*\b'
    words = re.findall(pattern, text)

    return sorted(set(words))


def find_context_with_symbol(text, symbol):
    pattern = r'.{0,30}' + re.escape(symbol) + r'.{0,30}'
    examples = re.findall(pattern, text)

    return sorted(set(examples))


def check_symbols():
    # path = '../data/final/para_kjh_ru.csv'  # mono_kjh para_kjh_ru
    path = '/home/adeshkin/Downloads/flores_dev_devtest_khakas/flores_dev_devtest_khakas/flores_dev_rus_kjh.csv'
    df = pd.read_csv(path)

    r_sents = df['rus'].tolist()
    k_sents = df['kjh'].tolist()

    r_text = ' '.join(r_sents)
    print(repr(''.join(sorted(set(r_text)))))
    print()

    k_text = ' '.join(k_sents)
    print(repr(''.join(sorted(set(k_text)))))
    print()

    assert 'ІіҒғңҷӦӧӰӱ' == 'ІіҒғңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ
    assert 'ІіҒғҢңҶҷӦӧӰӱ' == 'ІіҒғҢңҶҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in 'OHA':
        # examples = find_word_with_symbol(r_text, symbol)
        examples = find_context_with_symbol(r_text, symbol)

        if len(examples) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(examples))
            # print(*examples, sep='\n')
            print(examples)
            print()


def check_lat_cyr_word():
    path = '../data/final/para_kjh_ru.csv'  # mono_kjh para_kjh_ru
    df = pd.read_parquet("hf://datasets/adeshkin/google-smol-en-ru-kjh/smolsent/train-00000-of-00001.parquet")
    df = pd.read_json('/home/adeshkin/khakas_projects/smol/smolsent/ru_ce.jsonl', lines=True)
    r_sents = df['src'].tolist()
    k_sents = df['trg'].tolist()

    find_lat_cyr_words(r_sents, print_latin=False)
    find_lat_cyr_words(k_sents, print_latin=False)


def check_lat_cyr_word1():
    df = pd.read_csv('/home/adeshkin/Downloads/diversity500_khakas.xlsx - Лист1.csv')
    r_sents = df['русский'].tolist()
    k_sents = df['хакасский'].tolist()

    find_lat_cyr_words(r_sents, print_latin=False)
    find_lat_cyr_words(k_sents, print_latin=False)

if __name__ == '__main__':
    # check_symbols()
    check_lat_cyr_word1()
