import re
import pandas as pd
import random

pd.set_option('display.max_colwidth', None)


def drop_dupl(df):
    duplicates = df[df.duplicated(subset='Хакасский')]
    print('duplicates "Хакасский":')
    print('-' * 10)
    print(duplicates['Хакасский'])
    print('-' * 10)
    print()
    df = df.drop_duplicates(subset='Хакасский')

    duplicates = df[df.duplicated(subset='Русский')]
    print('duplicates "Русский":')
    print('-' * 10)
    print(duplicates['Русский'])
    print('-' * 10)
    print()
    df = df.drop_duplicates(subset='Русский')

    return df


def find_words_with_symbol(text, symbol):
    words = re.findall(r'\b\w*' + re.escape(symbol) + r'\w*\b', text)
    return sorted(set(words))[:10]


def re_sub_kjh(x):
    old_new_dict = {'ö': 'ӧ', 'ÿ': 'ӱ', 'ӊ': 'ң', 'Ӏ': 'І', 'Ӳ': 'Ӱ'}

    for ch1, ch2 in old_new_dict.items():
        x = re.sub(ch1, ch2, x)
        x = re.sub(ch1.upper(), ch2.upper(), x)

    return x


def re_sub_kjh_part2(x):
    old_new_dict = {'ӊ': 'ң'}

    for ch1, ch2 in old_new_dict.items():
        x = re.sub(ch1, ch2, x)
        x = re.sub(ch1.upper(), ch2.upper(), x)

    return x


def replace_ones_with_i(text):
    # Улучшенное регулярное выражение для всех возможных случаев
    pattern = r"(?<=\w)1|1(?=\w)"
    replacement = "і"

    # Замена
    result = re.sub(pattern, replacement, text)

    return result


def main2():
    path = 'data/corpus_final.csv'
    df = pd.read_csv(path)
    perevodchiki_done = ['Тюкпиекова Елена Яковлевна', 'Челтыгмашев Юрий Петрович',
                         'Кайдачакова Алевтина Петровна', 'Майнагашева Эльза Константиновна',
                         'Идимешева Ирина Васильевна', 'Казанаева Татьяна Федоровна',
                         'Тютюбеева Татьяна Евгеньевна', 'Сагалакова Надежда Николаевна',
                         'Тормозакова Нелля Васильевна', 'Сагатаева Елена Петровна',
                         'Улугбашева Олеся Илларионовна', 'Чертыков Антон Сергеевич']

    df['not_valid'] = df['Переводчик'].apply(lambda x: x in perevodchiki_done)
    print(len(df))
    df1 = df[~df['not_valid']]
    print(len(df1))
    df1['with_['] = df1.apply(lambda x: bool(re.search(r'[\(\(]', x['Хакасский']))
                                        and (not bool(re.search(r'[\(\(]', x['Русский']))), axis=1)
    df1 = df1[df1['with_[']]
    print(len(df1[df1['with_[']]))

    #df1['with_['] = df1.apply(lambda x: '[' in x['Хакасский'], axis=1)
    #print(len(df1))
    pairs = df1[['Русский', 'Хакасский']].values.tolist()
    df1 = pd.DataFrame(pairs, columns=['Русский', 'Хакасский'])
    df1['Хакасский'] = df1['Хакасский'].apply(lambda x: replace_ones_with_i(x))
    df1.to_csv('data/sentences_with_(.csv', index=False)
    #print(df1.head())


def main():
    path = 'data/part2 - 1.csv'
    df = pd.read_csv(path)
    df.dropna(subset=['Хакасский'], inplace=True)

    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    df = drop_dupl(df)
    #
    df['len_kjh'] = df.apply(lambda x: len(re.findall(r'\b\w{2,}\b', x['Хакасский'])), axis=1)
    df['len_rus'] = df.apply(lambda x: len(re.findall(r'\b\w{2,}\b', x['Русский'])), axis=1)

    df['not_valid'] = df.apply(lambda x: x['len_kjh'] < 2 and x['len_rus'] > 4, axis=1)
    print(df[df['not_valid']][['Русский', 'Хакасский']])
    print()

    print(len(df))
    df = df[~df['not_valid']]
    print(len(df))
    print()

    df['Хакасский'] = df['Хакасский'].apply(lambda x: re_sub_kjh_part2(x))
    text = ' '.join(df['Хакасский'].tolist())
    print(repr(''.join(sorted(set(text)))), '\n')
    assert 'іҒғҢңҷӦӧӰӱ' == 'іҒғҢңҷӦӧӰӱ'  # 'ІіҒғҢңҶҷӦӧӰӱ'

    for symbol in 'è':
        words = find_words_with_symbol(text, symbol)
        if len(words) > 0:
            print(symbol)
            print(len(words))
            print(words)
            print()

    df.to_csv(f'data/part2_all.csv', index=False)
    pairs = df[['Русский', 'Хакасский']].values.tolist()
    per_doc = 850
    for i in range(0, len(pairs), per_doc):
        df1 = pd.DataFrame(pairs[i:i + per_doc], columns=['Русский', 'Хакасский (Редактор)'])
        df1['Хакасский (Переводчик)'] = df1['Хакасский (Редактор)']
        df1.to_csv(f'data/part2_{i // per_doc}.csv', index=False, header=False)


if __name__ == '__main__':
    main2()
