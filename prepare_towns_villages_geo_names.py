import pandas as pd
import re
import unicodedata


def find_words_with_symbol(text, symbol):
    words = re.findall(r'\b\w*' + re.escape(symbol) + r'\w*\b', text)
    # words = re.findall(r'.{0,15}' + re.escape(symbol) + r'.{0,15}', text)
    return sorted(set(words))


def main():
    path = '/home/adeshkin/Downloads/населенные пункты РХ - населенные пункты РХ.csv'
    df = pd.read_csv(path)
    df['Хакасский'] = df['Хакасский'].apply(lambda x: x.replace('K', 'К').replace('i', 'і'))
    print(df[~df['Хакасский'].str.isupper()])

    text = ' '.join(df['ru_short'].tolist())
    print(repr(''.join(sorted(set(text)))))
    # assert 'іғңҷӦӧӰӱ' == 'іғңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ
    #
    df['ru_short'] = df['Русский'].apply(lambda x: re.sub(r'\b(г\.|с\.|д\.|п\.|аал|ст\.|пгт\.)\s+', '', x))
    df['kjh_short'] = df['Хакасский'].apply(lambda x: re.sub(r'\b(г\.|п\.|аалы|аал|гтп|п\.ст\.|п\. ст\.)$', '', x))
    df['Русский'] = df['Русский'].apply(lambda x: re.sub(r'\.([^\s])', r'. \1', x))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: re.sub(r'\.([^\s])', r'. \1', x))
    print(df[~df['ru_short'].apply(lambda x: str(x)[0].isupper() if pd.notnull(x) and len(str(x)) > 0 else False)])


    for symbol in 'Ki':
        print(repr(symbol))
        print(unicodedata.name(symbol))
        print(repr(find_words_with_symbol(text, symbol)))

    df.to_csv(path.replace('.csv', '_fix.csv'), index=False)


if __name__ == '__main__':
    main()
