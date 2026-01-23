import pandas as pd
import re
import unicodedata


def find_words_with_symbol(text, symbol):
    words = re.findall(r'\b\w*' + re.escape(symbol) + r'\w*\b', text)
    # words = re.findall(r'.{0,15}' + re.escape(symbol) + r'.{0,15}', text)
    return sorted(set(words))


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


def find_lat_cyr_words(kjh_sents):
    lat_words, lat_cyr_words = analyze_words(kjh_sents)
    print('Latin-cyrillic words')
    print(len(lat_cyr_words))
    for word in lat_cyr_words:
        print(word)
        for ch in word:
            print(ch, unicodedata.name(ch))


def main():
    path = '/home/adeshkin/khakas_projects/data/translation/test_corpus_yandex/test_yandex_clean.csv'
    df = pd.read_csv(path)
    kjh_sents = df['kjh'].values.tolist()
    find_lat_cyr_words(kjh_sents)

    text = ' '.join(kjh_sents)
    print(repr(''.join(sorted(set(text)))))
    #
    # assert 'іғңҷӦӧӰӱ' == 'іғңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ
    #
    # for symbol in 'абвгдежзийклмнопрстуфхцчшщъыьэюяёіғңҷӧӱ':
    #     words = find_words_with_symbol(text, symbol)
    #     if len(words) > 0:
    #         print(repr(symbol))
    #         print(unicodedata.name(symbol))
    #         print(len(words))
    #         print(*words, sep='\n')
    #         print()
    sorted_df = df.sort_values(by='kjh', key=lambda x: x.str.len())
    sorted_df.to_csv(path.replace('.csv', '_sorted.csv'), index=False)


if __name__ == '__main__':
    main()

