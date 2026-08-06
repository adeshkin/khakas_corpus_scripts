import pandas as pd
import re
import unicodedata

from prepare_smol import fix_symbols


def find_words_with_symbol(text, symbol):
    # words = re.findall(r'\b\w*' + re.escape(symbol) + r'\w*\b', text)
    words = re.findall(r'.{0,15}' + re.escape(symbol) + r'.{0,15}', text)
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


import os
import pandas as pd
import re
import unicodedata

latin_pattern = re.compile(r'[a-zA-Z]')
cyrillic_pattern = re.compile(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]')


def count_unique_chars(word):
    latin_chars = set(latin_pattern.findall(word.lower()))
    cyrillic_chars = set(cyrillic_pattern.findall(word.lower()))

    return len(latin_chars), len(cyrillic_chars)


def replace_lat_cyr_v1_kjh(text):
    def replace_match(match):
        word = match.group(0)

        lat_count, cyr_count = count_unique_chars(word)

        if lat_count == 1 and 'i' in word and cyr_count > lat_count:
            word = word.replace('i', 'і')

        return word

    pattern = r'[a-zA-Zа-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]+'
    return re.sub(pattern, replace_match, text)




def main():
    path = '/home/adeshkin/khakas_projects/data/translation/test_corpus_yandex/test_yandex_clean.csv'
    path = '/home/adeshkin/khakas_projects/khakas_corpus_scripts/smol/smoldoc/smoldoc_kjh.csv'
    # path = '/home/adeshkin/Downloads/smolsent_final.csv'
    df = pd.read_csv(path)
    df = df.fillna('')
    # df['kjh'] = df['kjh'].apply(lambda x: replace_lat_cyr_v1_kjh(x).replace('чоx', 'чох').replace('иткeні', 'иткені').replace('cookiе', 'cookie').replace('ҷi', 'ҷі'))
    kjh_sents = df['en'].values.tolist()

    find_lat_cyr_words(kjh_sents)

    text = ' '.join(kjh_sents)
    print(repr(''.join(sorted(set(text)))))
    #
    assert 'ІіғңҷӦӧӰӱ' == 'ІіғңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ
    #
    # for symbol in 'AEFGHJKLMNPSTWYabcdefghiklmnoprstuvwxyz':
    #     words = find_words_with_symbol(text, symbol)
    #     if len(words) > 0:
    #         print(repr(symbol))
    #         print(unicodedata.name(symbol))
    #         print(len(words))
    #         print(*words, sep='\n')
    #         print()
    # sorted_df = df.sort_values(by='kjh', key=lambda x: x.str.len())
    # sorted_df.to_csv(path.replace('.csv', '_sorted.csv'), index=False)
    # df.to_csv('/home/adeshkin/Downloads/smolsent_final_fix.csv', index=False)

def main1():
    df = pd.read_csv('/home/adeshkin/Downloads/common_voice - life.csv')
    df = df.dropna()
    df = df.fillna('')
    df['Хакасский'] = df['Хакасский'].apply(lambda x: x.replace('A', 'А').replace('C', 'С').replace('i', 'і').replace('I', 'І').replace('a', 'а').replace('c', 'с').replace('e', 'е').replace('p', 'р').replace('y', 'у').replace('Ö', 'Ӧ').replace('симіє', 'симіс').replace('«', '"').replace('»', '"').replace('‒', '-').replace('–', '-').replace('—', '-'))
    kjh_sents = df['Хакасский'].values.tolist()
    text = ' '.join(kjh_sents)
    print(repr(''.join(sorted(set(text)))))

    assert 'ІіғңҷӦӧӰӱ' == 'ІіғңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ
    # find_lat_cyr_words(kjh_sents)
    #
    for symbol in '‒–—':
        words = find_words_with_symbol(text, symbol)
        if len(words) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(words))
            print(*words, sep='\n')
            print()
    df.to_csv('/home/adeshkin/Downloads/common_voice - life_fix.csv', index=False)
if __name__ == '__main__':
    main1()

