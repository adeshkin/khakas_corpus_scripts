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


def count_unique_chars(word):
    latin_chars = set(re.findall(r'[a-zA-Z]', word.lower()))
    cyrillic_chars = set(re.findall(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]', word.lower()))

    return len(latin_chars), len(cyrillic_chars)


# old_new_dict = {'ö': 'ӧ',
#                     'ÿ': 'ӱ',
#                     'ӊ': 'ң',
#                     'Ӏ': 'І',
#                     'Мanagement': 'Management',
#                     'А1GP': 'A1GP',
#                     'iкi': 'ікі',
#                     'АОL': 'AOL',
#                     'Iкi': 'Ікі',
#                     'cellа': 'cella',
#                     'СafeNet': 'CafeNet',
#                     'ҷi': 'ҷі',
#                     'Аpollo': 'Apollo',
#                     'Коnami': 'Konami',
#                     'COVІD': 'COVID',
#                     'АNSA': 'ANSA'
#                     }

def replace_symbols(text):
    old_new_dict = {'\xa0': ' ',
                    'ö': 'ӧ',
                    'ÿ': 'ӱ',
                    'ӊ': 'ң',
                    'Ӏ': 'І',
                    'ӌ': 'ҷ',
                    'iкi': 'ікі',
                    'iс': 'іс',
                    'ХIV': 'XIV',
                    'ХI': 'XI',
                    }

    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def fix_mixed_letters_i_c(text):
    def replace_match(match):
        word = match.group(0)

        lat_count, cyr_count = count_unique_chars(word)
        if lat_count == 1 and 'i' in word and cyr_count > lat_count:
            word = word.replace('i', 'і')
        if lat_count == 1 and 'c' in word and cyr_count > lat_count:
            word = word.replace('c', 'с')
        if lat_count == 1 and 'I' in word and cyr_count > lat_count:
            word = word.replace('I', 'І')
        if lat_count == 1 and 'C' in word and cyr_count > lat_count:
            word = word.replace('C', 'С')
        if lat_count == 2 and 'i' in word and 'c' in word and cyr_count > lat_count:
            word = word.replace('i', 'і').replace('c', 'с')

        return word

    pattern = r'[a-zA-Zа-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]+'
    return re.sub(pattern, replace_match, text)


def find_lat_cyr_words(kjh_sents):
    lat_words, lat_cyr_words = analyze_words(kjh_sents)
    print('Latin-cyrillic words')
    for word in lat_cyr_words:
        latin_chars = set(re.findall(r'[a-zA-Z]', word))
        cyrillic_chars = set(re.findall(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]', word))
        print(word)
        print(latin_chars)
        print(cyrillic_chars)
        print()
    print(len(lat_cyr_words))


def main():
    path = '/home/adeshkin/khakas_projects/data/translation/flores/flores_devtest - 1.csv'
    df = pd.read_csv(path)
    df.rename(columns={'Русский': 'rus', 'Хакасский (Редактор)': 'kjh'}, inplace=True)
    df['kjh'] = df['kjh'].apply(lambda x: replace_symbols(x))
    df['kjh'] = df['kjh'].apply(lambda x: fix_mixed_letters_i_c(x))
    kjh_sents = df['kjh'].values.tolist()

    find_lat_cyr_words(kjh_sents)

    text = ' '.join(kjh_sents)
    print(repr(''.join(sorted(set(text)))))

    assert 'ІіғңҷӦӧӰӱ' == 'ІіғңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in '':
        words = find_words_with_symbol(text, symbol)
        if len(words) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(words))
            # print(*words, sep='\n')
            print(words)
            print()

    df.to_csv(path.replace('.csv', '_clean.csv'))
    sorted_df = df.sort_values(by='kjh', key=lambda x: x.str.len())
    sorted_df.to_csv(path.replace('.csv', '_sorted.csv'), index=False)


if __name__ == '__main__':
    main()
