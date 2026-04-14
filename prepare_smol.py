import pandas as pd
import re


def main():
    df = pd.read_csv('/home/adeshkin/Downloads/smolsent_kjh - Sheet1.csv')
    # df = df.fillna('')
    # df = df.dropna(subset=['Translation АНИСИМОВ'])
    df['Translation АНИСИМОВ'] = df['Translation АНИСИМОВ'].apply(lambda x: re.sub(r'[^\w]|_', '', x.strip().replace(' ', '')))
    df['Русский'] = df['Русский'].apply(lambda x: re.sub(r'[^\w]|_', '', x.strip().replace(' ', '')))
    print(len(df[df['Translation АНИСИМОВ'] != df['Русский']][['Translation АНИСИМОВ', 'Русский']].values))
    print(df[df['Translation АНИСИМОВ'] != df['Русский']][['Translation АНИСИМОВ', 'Русский']].values)

    # kjh_df = pd.read_csv('/home/adeshkin/Downloads/Чебочакова Ирина Максимовна - 2026 - Copy of smolsent.csv')
    # # kjh_df = kjh_df.dropna(subset=['Русский'])
    # kjh_df = kjh_df.fillna('')
    # mapping = kjh_df.set_index('Русский')['Хакасский (Редактор)']
    #
    # df['kjh'] = df['Translation АНИСИМОВ'].map(mapping)
    # df = df.rename(columns={'Хакасский (Редактор)': 'kjh'})
    # df = df[['en', 'Translation АНИСИМОВ', 'kjh']]
    # df.to_csv('/home/adeshkin/Downloads/smolsent_kjh_for_pre.csv', index=False)


def find_word_with_symbol(text, symbol):
    pattern = r'\b\w*' + re.escape(symbol) + r'\w*\b'
    words = re.findall(pattern, text)

    return sorted(set(words))


def find_context_with_symbol(text, symbol):
    pattern = r'.{0,15}' + re.escape(symbol) + r'.{0,15}'
    examples = re.findall(pattern, text)

    return sorted(set(examples))


def fix_symbols():
    df = pd.read_csv('/home/adeshkin/Downloads/smoldoc_kjh_for_pre.csv')

    examples = df['kjh'].tolist()
    text = ' '.join(examples)
    print(repr(''.join(sorted(set(text)))))
    print()
    assert 'ІіҒғңҷӦӧӰӱ' == 'ІіҒғңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    print_max = 20
    for symbol in 'ӏ':
        # examples = find_word_with_symbol(text, symbol)
        examples = find_context_with_symbol(text, symbol)

        if len(examples) > 0:
            print(repr(symbol))
            if len(symbol) == 1:
                print(unicodedata.name(symbol))
            print(len(examples))
            if print_max:
                print(examples[:print_max])
            else:
                print(examples)
                # print(*examples, sep='\n')
            print()


if __name__ == '__main__':
    main()
