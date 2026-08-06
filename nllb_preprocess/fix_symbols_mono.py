import re
import os
import pandas as pd
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
    pattern = r'.{0,15}' + re.escape(symbol) + r'.{0,15}'
    examples = re.findall(pattern, text)

    return sorted(set(examples))


def replace_mono_kjh(text):
    old_new_dict = {
        'кeнӧрткі': 'кӱнӧрткі',
        'кeнде': 'кӱнде',
        'тӧгібісчеңңeр': 'тӧгібісчеңнeр',
        'eс': 'ӱс',
        'Сіpepre': 'Сіpepгe',
        'travelсайт': 'travel сайт',
        'Пaба-іҷелeрнен': 'Пaба-іҷелeрнең',
        'пeдіріл': 'пӱдіріл',
        'eн': 'ӱн',
        'Cӧ6іpe': 'Cӧбіpe',
        'пeeл': 'пӱӱл',
        'eчeн': 'ӱчӱн',
        'кeскec': 'кӱскӱc',
        'тоғынарғаDark-іceтехника': 'тоғынарға Dark - іce техника',
        'Іdentіty': 'Identity',

        'cjс': 'сӧс',
        'Johnsonвакциналарнаң': 'Johnson вакциналарнаң',
        'bдjк': 'ідӧк',
        'Jjнb': 'Ӧӧні',

        'Пy': 'Пу',
        'LADA-ХRАY': 'LADA-XRAY',
        'табыuларныy': 'табығларның',
        'cіtyАғбанның': 'cіty Ағбанның',
        'жyрналның': 'журналның',
        'yаndех': 'yandex',
        'tyзы': 'тузы',
        'чyртағҷыларынаң': 'чуртағҷыларынаң',
        'тимнӱнҷeңнeр': 'тимненҷеңнер',

        'кӱскec': 'кӱскӱс',
        'чӧитеичeбіс': 'чӧптепчебіс',
        'eчӱн': 'чӧптепчебіс',
        'Пeӱн': 'Пӱӱн',
        'lіfeофициальнай': 'lіfe официальнай',
        'ОРНЫХЧАТХАНPROPERZІКОМПЛЕКСНЕҢ': 'ОРНЫХЧАТХАН PROPERZІ КОМПЛЕКСНЕҢ',

        'Gғrғ': 'Guru',
        'ruсайт': 'ru сайт',
        'Добро Start': 'Guru',
        'почтазарstranahabar': 'почтазар stranahabar',
        'Tourосхас': 'Tour осхас',
        'ruРоссиядағы': 'ru Россиядағы',

        'истерre': 'истерге',
        'пиpep': 'пирер',

        'KӰHHEҢ': 'КӰННЕҢ',
        'KӰ3ІHEҢ': 'КӰЗІНЕҢ',
        'киpee': 'кирее',
        'тилідерre': 'тилідерге',
        'TУPИCTTEPHІҢ': 'ТУРИСТТЕРНІҢ',
        'TӰ3EP': 'ТӰЗЕР',
        'піpep': 'пірер',
        'ӰГРЕТЧІЛEPІHІҢ': 'ӰГРЕТЧІЛЕРІНІҢ',
        'KI3IЛEP': 'КІЗІЛЕР',
        'Cӧбіpe': 'Сӧбіре',
        'Сіpepгe': 'Сірерге',
        'bкbнxb': 'ікінҷі',

        'табыuxылар': 'табығҷылар',
        'чуртаuxылары': 'чуртағҷылары',
        'суuxыларым': 'суғҷыларым',

        'Алынxа': 'Алынҷа',
        'Xакасиядан': 'Хакасиядаң',
        'XІ': 'XI',
        'XXXІІ': 'XXXII',
        'санаxаң': 'санаҷаң',
        'нааxылалған': 'нааҷылалған',
        'XІІ': 'XII',
        'xі': 'ҷі',
        'чӧрxең': 'чӧрҷең',
        'XXІІ': 'XXII',
        'одырxаң': 'одырҷаң',
        'XXІІІ': 'XXIII',
        'XІX': 'XIX',
        'XXІ': 'XXI',
        'ІX': 'IX',
        'XІІІ': 'XIII',
        'XXXІ': 'XXXI',
        'нинxе': 'нинҷе',

        'XУC': 'ХУС',

        'Breҷit': 'Brexit',
        'Bдӧк': 'Ідӧк',
        'Bладимировна': 'Владимировна',
        'VІІІ': 'VIII',
        'кулmт': 'культ',
        'июлm': 'июль',

        'Сибирm': 'Сибирь',
        'ІKІ': 'ІКІ',
        'VІ': 'VI',
        'ІV': 'IV',
        'ӦKІС': 'ӦКІС',
    }
    # ІіҒғҢңҶҷӦӧӰӱ
    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text.strip()


def replace_lat_cyr_mono_kjh(text):
    def replace_match(match):
        word = match.group(0)

        lat_count, cyr_count = count_unique_chars(word)

        if lat_count == 1 and 'F' in word and cyr_count > lat_count:
            word = word.replace('F', 'Ғ')

        if lat_count == 1 and 'X' in word and cyr_count > lat_count:
            word = word.replace('X', 'Х')

        if lat_count == 1 and 'e' in word and cyr_count > lat_count:
            word = word.replace('e', 'е')

        if lat_count == 1 and 'M' in word and cyr_count > lat_count:
            word = word.replace('M', 'М')

        if lat_count == 1 and 'c' in word and cyr_count >= lat_count:
            word = word.replace('c', 'с')

        if lat_count == 1 and 'C' in word and cyr_count >= lat_count:
            word = word.replace('C', 'С')

        if lat_count == 1 and 'u' in word and cyr_count > lat_count:
            word = word.replace('u', 'ғ')

        if lat_count == 1 and 'p' in word and cyr_count > lat_count:
            word = word.replace('p', 'р')

        if lat_count == 1 and 'E' in word and cyr_count > lat_count:
            word = word.replace('E', 'Е')

        if lat_count == 1 and 'o' in word and cyr_count > lat_count:
            word = word.replace('o', 'о')

        if lat_count <= 2 and 'a' in word and cyr_count >= lat_count:
            word = word.replace('a', 'а')

        if lat_count <= 2 and 'y' in word and cyr_count >= lat_count:
            word = word.replace('y', 'ң')

        if lat_count <= 2 and 'b' in word and cyr_count > lat_count:
            word = word.replace('b', 'і')

        if lat_count == 1 and 'j' in word and cyr_count > lat_count:
            word = word.replace('j', 'ӧ')


        # ІіҒғҢңҶҷӦӧӰӱ

        if cyr_count <= 2 and 'і' in word and lat_count > cyr_count:
            word = word.replace('і', 'i')

        if cyr_count <= 2 and 'І' in word and lat_count > cyr_count:
            word = word.replace('І', 'I')

        if cyr_count == 1 and 'о' in word and lat_count > cyr_count:
            word = word.replace('о', 'o')

        if cyr_count == 1 and 'р' in word and lat_count > cyr_count:
            word = word.replace('р', 'p')

        return word

    text = re.sub(r'\b\w+\b', replace_match, text)
    return text.strip()


def fix_mono():
    path = '../data/mono_kc_rn_at.csv'
    save_path = '../data/mono_fix_symbols.csv'
    assert not os.path.exists(save_path)
    df = pd.read_csv(path)

    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_mono_kjh(x))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_lat_cyr_mono_kjh(x))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_lat_cyr_mono_kjh(x))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_mono_kjh(x))

    sents = df['Хакасский'].tolist()

    text = ' '.join(sents)
    print(repr(''.join(sorted(set(text)))))
    print()

    find_lat_cyr_words(sents, print_latin=False)

    assert 'ІіҒғҢңҶҷӦӧӰӱ' == 'ІіҒғҢңҶҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in '':
        # examples = find_word_with_symbol(text, symbol)
        examples = find_context_with_symbol(text, symbol)

        if len(examples) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(examples))
            # print(*examples, sep='\n')
            print(examples)
            print()

    df.to_csv(save_path, index=False)


if __name__ == '__main__':
    fix_mono()
