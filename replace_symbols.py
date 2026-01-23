import pandas as pd
import re
import unicodedata


def find_words_with_symbol(text, symbol):
    words = re.findall(r'\b\w*' + re.escape(symbol) + r'\w*\b', text)
    return sorted(set(words))


def replace_symbols(text):
    old_new_dict = {'ö': 'ӧ'}

    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def main():
    path = '/home/adeshkin/khakas_projects/data/translation/test_corpus_yandex/test_yandex.csv'
    df = pd.read_csv(path)
    df.rename(columns={'Русский': 'rus', 'Хакасский (Ирина Максимовна Чебочакова)': 'kjh'}, inplace=True)
    df['kjh'] = df['kjh'].apply(lambda x: replace_symbols(x))
    text = ' '.join(df['kjh'].values.tolist())
    print(repr(''.join(sorted(set(text)))))

    assert 'іғңҷӦӧӰӱ' == 'іғңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in '²':
        words = find_words_with_symbol(text, symbol)
        if len(words) > 0:
            print(symbol)
            print(unicodedata.name(symbol))
            print(len(words))
            print(words)
            print()


if __name__ == '__main__':
    main()
