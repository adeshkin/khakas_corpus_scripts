import pandas as pd
import re

def find_words_with_symbol(text, symbol):
    words = re.findall(r'\b\w*' + re.escape(symbol) + r'\w*\b', text)
    words_new = [x for x in words if bool(re.search(r'[А-Яа-яІіҒғҢңҶҷӦӧӰӱ]', x))]
    return sorted(set(words_new))


def re_sub_kjh(text):
    # old_new_dict = {'ö': 'ӧ', 'ÿ': 'ӱ', 'ӊ': 'ң', 'Ӏ': 'І', 'Ӳ': 'Ӱ'}
    old_new_dict = {'ӊ': 'ң', 'i': 'і'}
    words = text.split()
    for i, word in enumerate(words):
        if bool(re.search(r'[А-Яа-яІіҒғҢңҶҷӦӧӰӱ]', word)):
            for ch1, ch2 in old_new_dict.items():
                word = re.sub(ch1, ch2, word)
                word = re.sub(ch1.upper(), ch2.upper(), word)
        text = text.replace(words[i], word)

    return text


def main():
    df = pd.read_csv('../data/vse_krome_kicheeva_part1_part2_[_( - 1.csv')

    print('before ', len(df))
    df['not_valid'] = df.apply(lambda x: len(str(x['Хакасский (Редактор)'])) < 5, axis=1)
    df = df[~df['not_valid']]
    print('after ', len(df))
    print()

    print('before ', len(df))
    df.dropna(subset=['Хакасский (Редактор)'], inplace=True)
    df.dropna(subset=['Русский'], inplace=True)
    print('after ', len(df))
    print()

    duplicates = df[df.duplicated(subset='Хакасский (Редактор)')]
    print('duplicates "Хакасский":')
    print('-' * 10)
    print(duplicates['Хакасский (Редактор)'])
    print('-' * 10)
    print()

    duplicates = df[df.duplicated(subset='Русский')]
    print('duplicates "Русский":')
    print(len(duplicates))
    print('-' * 10)
    print(duplicates['Русский'])
    print('-' * 10)
    print()

    df['not_valid'] = df.apply(lambda x: not re.search(r'[А-Яа-яІіҒғҢңҶҷӦӧӰӱ]', str(x['Хакасский (Редактор)'])), axis=1)
    print(df[df['not_valid']][['Русский', 'Хакасский (Редактор)']])
    print()

    df['not_valid'] = df.apply(lambda x: not re.search(r'[А-Яа-я]', str(x['Русский'])), axis=1)
    print(df[df['not_valid']][['Русский', 'Хакасский (Редактор)']])
    print()

    df['Хакасский (Редактор)'] = df['Хакасский (Редактор)'].apply(lambda x: re.sub(r'―', '—', x))
    df['Хакасский (Редактор)'] = df['Хакасский (Редактор)'].apply(lambda x: re.sub(r'–', '—', x))
    df['Хакасский (Редактор)'] = df['Хакасский (Редактор)'].apply(lambda x: re_sub_kjh(x))

    text = ' '.join(df['Хакасский (Редактор)'].tolist())
    print(repr(''.join(sorted(set(text)))), '\n')

    # import unicodedata
    #
    # print(unicodedata.name('-'))
    # print(unicodedata.name('—'))
    #
    #
    # df['hor_bar'] = df.apply(lambda x: bool(re.search(r'[–]', str(x['Хакасский (Редактор)']))), axis=1)
    # print(df[df['hor_bar']][['Русский', 'Хакасский (Редактор)']])
    # print()

    # assert 'іҒғҢңҷӦӧӰӱ' == 'іҒғҢңҷӦӧӰӱ'  # 'ІіҒғҢңҶҷӦӧӰӱ'
    #
    for symbol in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        words = find_words_with_symbol(text, symbol)
        if len(words) > 0:
            print(symbol)
            print(len(words))
            print(words)
            print()

if __name__ == '__main__':
    import unicodedata
    print(unicodedata.name('y'))
