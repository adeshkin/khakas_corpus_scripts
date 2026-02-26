import pandas as pd
import re
import unicodedata
from bs4 import BeautifulSoup


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
        try:
            words = re.findall(r'\b\w+\b', sentence)
        except TypeError:
            print(sentence)
            continue

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
    print('Latin')
    print(lat_words)

    print('Latin-cyrillic words')
    for word in lat_cyr_words:
        latin_chars = set(re.findall(r'[a-zA-Z]', word))
        cyrillic_chars = set(re.findall(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]', word))
        print(word)
        print(latin_chars)
        print(cyrillic_chars)
        print()
    print(len(lat_cyr_words))


def replace_symbols(text):
    old_new_dict = {
        'ӌ': 'ҷ',
        'Ӌ': 'Ҷ',
        'A': 'А',
        'C': 'С',
        'E': 'Е',
        'F': 'Ғ',
        'H': 'Н',
        'K': 'К',
        'M': 'М',
        'O': 'О',
        'T': 'Т',
        'Ӏ': 'І',
        'Ӊ': 'Ң',
        'ӊ': 'ң',
        'ÿ': 'ӱ',
        'à': '◊',
        'Ö': 'Ӧ',
        '\x8e': '',
        '\x96': '',
        '\xa0': ' ',
        '\xad': '',
        '\u206a': '',
        'P': 'Р',
        'NРI': 'NPI',
        'X': 'Х',
        'ХIХ': 'XIX',
        'upoн': 'ирон',
        'чапчаy': 'чапчаң',
        'мирxең': 'мирҷең',
        'пic': 'піс',
        'пip': 'пір',
        'npил': 'прил',
        'IКI': 'ІКІ',
        'IС': 'ІС',
        'НIН': 'НІН',
        'гi': 'гі',
        'бi': 'бі',
        'oт': 'от',
        'eс': 'ес',
        'дee': 'дее',
        'cyғ': 'суғ',
        'ілдіpepre': 'ілдірерге',
        'суух': 'суух',
        'apaғa': 'араға',
        'уpap': 'урар',
        'полғan': 'полған',
        'cooп': 'сооп',
        'cmeнaa': 'стенаа',
        'пеpeн': 'перен',
        'оm': 'от',
        'кipген': 'кірген',
        'cyуx': 'суух',
        'комисcap': 'комиссар',
        'разy': 'разу',
        'Аcc': 'Acc',
        'мӱнlӱргес': 'мӱндӱргес',
        'ax': 'ах',
        ' a ': '◊',
        'nip': 'пір',
        'coop': 'соор',
        'cap': 'сар',
        'copra': 'сорга',
        'smallсарs': 'smallcaps',
        'mac': 'мас',
        'owe': 'же',
        'cjtsatfftfed': ' ',
        'mil': 'тіл',
        'cvy': 'суу',
        '-ri': '-гі',
        ' up': ' ир',
        ' a': ' ◊ ',
        r'<sub>\(</sub>ц': ' ',
        '&lt;': ' ',
        'саларына<u>ң</u>': 'саларынаң',
        '</b>a<b>': '</b> ◊ <b>',
        'V1': 'V 1',
        r'\\B': ' ',
    }

    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def count_unique_chars(word):
    latin_chars = set(re.findall(r'[a-zA-Z]', word.lower()))
    cyrillic_chars = set(re.findall(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]', word.lower()))

    return len(latin_chars), len(cyrillic_chars)


def fix_mixed_letters_i_c(text):
    def replace_match(match):
        word = match.group(0)

        lat_count, cyr_count = count_unique_chars(word)
        if lat_count == 1 and 'i' in word and cyr_count > lat_count:
            word = word.replace('i', 'і')
        if lat_count == 1 and 'i' in word and cyr_count == lat_count:
            word = word.replace('i', 'і')
        if lat_count == 1 and 'e' in word and cyr_count > lat_count:
            word = word.replace('e', 'е')
        if lat_count == 1 and 'a' in word and cyr_count > lat_count:
            word = word.replace('a', 'а')
        if lat_count == 1 and 'a' in word and cyr_count > lat_count:
            word = word.replace('a', 'а')
        if lat_count == 1 and 'u' in word and cyr_count > lat_count:
            word = word.replace('u', 'ғ')
        if lat_count == 1 and 'n' in word and cyr_count > lat_count:
            word = word.replace('n', 'п')
        if lat_count == 1 and 'c' in word and cyr_count > lat_count:
            word = word.replace('c', 'с')
        if lat_count == 1 and 'I' in word and cyr_count > lat_count:
            word = word.replace('I', 'І')
        if lat_count == 1 and 'I' in word and cyr_count == lat_count:
            word = word.replace('I', 'І')
        if lat_count == 1 and 'C' in word and cyr_count > lat_count:
            word = word.replace('C', 'С')
        if lat_count == 2 and 'i' in word and 'c' in word and cyr_count > lat_count:
            word = word.replace('i', 'і').replace('c', 'с')

        return word

    pattern = r'[a-zA-Zа-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]+'
    return re.sub(pattern, replace_match, text)


def remove_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    for span in soup.find_all("span", variant="smallcaps"):
        span.unwrap()
    for tag_name in ["sup", "big"]:
        for tag in soup.find_all(tag_name):
            tag.unwrap()

    text = str(soup)

    while re.search(r'<b>\s*</b>', text):
        text = re.sub(r'<b>\s*</b>', ' ', text)

    return text

def main():
    df = pd.read_csv('/home/adeshkin/Downloads/hrs_new34.csv')
    df['field1_fixed'] = df['field1'].apply(lambda x: replace_symbols(x))
    df['field1_fixed'] = df['field1_fixed'].apply(lambda x: fix_mixed_letters_i_c(x))
    df['field1_fixed_tags'] = df['field1_fixed'].apply(lambda x: remove_tags(x))
    df['word_fixed'] = df['word'].apply(lambda x: fix_mixed_letters_i_c(x).lower().replace('ӌ', 'ҷ'))
    df['semgloss_fixed'] = df['semgloss'].apply(
        lambda x: x.lower().replace('ӌ', 'ҷ').replace('ссорnться', 'ссориться').replace('позволятm',
                                                                                        'позволять').replace('cоюз',
                                                                                                             'союз'))

    field1s = df['field1_fixed_tags'].values.tolist()

    df[['word_fixed', 'semgloss_fixed', 'field1_fixed', 'field1_fixed_tags']].to_csv('/home/adeshkin/Downloads/hrs_new34_word_field1_semgloss_fixed_tags.csv', index=False)

    find_lat_cyr_words(field1s)

    text = ' '.join(field1s)
    print(repr(''.join(sorted(set(text)))))
    assert 'іғңҷӧӱ' == 'іғңҷӧӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in ['<і>', '<І>', '</і>', '</І>']:
        words = find_words_with_symbol(text, symbol)
        if len(words) > 0:
            print(repr(symbol))
            # print(unicodedata.name(symbol))
            print(len(words))
            print(*words, sep='\n')
            print()


if __name__ == '__main__':
    main()
