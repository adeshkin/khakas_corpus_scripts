import pandas as pd
import re
import unicodedata


def find_words_with_symbol(text, symbol):
    words = re.findall(r'\b\w*' + re.escape(symbol) + r'\w*\b', text)
    # words = re.findall(r'.{0,15}' + re.escape(symbol) + r'.{0,15}', text)

    return sorted(set(words))


def main():
    path = '/home/adeshkin/khakas_projects/data/translation/flores/flores_dev - 1.csv'
    df = pd.read_csv(path)
    df.rename(columns={'Русский': 'rus', 'Хакасский (Редактор)': 'kjh'}, inplace=True)
    kjh_sents = df['kjh'].values.tolist()
    text = ' '.join(kjh_sents)
    print(repr(''.join(sorted(set(text)))))

    # assert 'іғңҷӦӧӰӱ' == 'ІіҒғҢңҶҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in 'ÕõöÿІ':
        words = find_words_with_symbol(text, symbol)
        if len(words) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(words))
            print(*words, sep='\n')
            print()


if __name__ == '__main__':
    main()
