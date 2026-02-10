import pandas as pd
import re
import unicodedata


def find_words_with_symbol(text, symbol):
    words = re.findall(r'\b\w*' + re.escape(symbol) + r'\w*\b', text)
    # words = re.findall(r'.{0,15}' + re.escape(symbol) + r'.{0,15}', text)

    return sorted(set(words))


def main():
    path = '/home/adeshkin/khakas_projects/data/translation/flores/flores_devtest - 1_clean - fixed.csv'
    df = pd.read_csv(path)
    # df.rename(columns={'Хакасский (Редактор)': 'kjh'}, inplace=True)
    kjh_sents = df['kjh'].values.tolist()
    text = ' '.join(kjh_sents)
    print(repr(''.join(sorted(set(text)))))

    assert 'ІіғңҷӦӧӰӱ' == 'ІіғңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in 'acioptm':
        words = find_words_with_symbol(text, symbol)
        if len(words) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(words))
            print(*words, sep='\n')
            print()

    # df.to_csv(path.replace('.csv', '_clean.csv'))
    # sorted_df = df.sort_values(by='kjh', key=lambda x: x.str.len())
    # sorted_df.to_csv(path.replace('.csv', '_sorted.csv'), index=False)


if __name__ == '__main__':
    main()
