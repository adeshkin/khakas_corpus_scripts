import pandas as pd
import difflib

pd.set_option('display.max_colwidth', None)


def main():
    df1 = pd.read_csv('/home/adeshkin/Downloads/smoldoc.csv')
    df1 = df1.fillna('')

    df2 = pd.read_csv('/home/adeshkin/Downloads/Чебочакова Ирина Максимовна - 2026 - Copy of smoldoc.csv')
    print(len(df2), len(df1))
    df2 = df2.fillna('')
    # print(df['Translation АНИСИМОВ'].head())
    # print(len(df))

    df = pd.read_csv('smoldoc_kjh.csv')
    df = df.fillna('')
    kjh_examples = df['kjh'].values.tolist()
    text = ' '.join(kjh_examples)
    print(repr(''.join(sorted(set(text)))))
    assert 'ІіғңҷӦӧӰӱ' == 'ІіғңҷӦӧӰӱ' # ІіҒғҢңҶҷӦӧӰӱ
    df = df.fillna('')

    df['Русский'] = df2['Русский']

    assert len(df1) == len(df)
    df['Translation АНИСИМОВ_orig'] = df1['Translation АНИСИМОВ']
    df['Translation АНИСИМОВ_orig'] = df['Translation АНИСИМОВ_orig'].apply(lambda x: x.strip())
    df['Translation АНИСИМОВ'] = df['Translation АНИСИМОВ'].apply(lambda x: x.strip())
    df['Русский'] = df['Русский'].apply(lambda x: x.strip())

    df['en_orig'] = df1['en']

    # print(df[df['en'] != df['en_orig']][['en', 'en_orig']].head())
    assert len(df[df['en'] != df['en_orig']]) == 0
    assert len(df[df['Translation АНИСИМОВ'] != df['Translation АНИСИМОВ_orig']]) == 0
    # bad_pairs = df[df['Translation АНИСИМОВ'] != df['Translation АНИСИМОВ_orig']][
    #     ['Translation АНИСИМОВ', 'Translation АНИСИМОВ_orig']].values.tolist()
    # bad_pairs = df[df['Translation АНИСИМОВ'] != df['Русский']][
    #     ['Translation АНИСИМОВ', 'Русский']].values.tolist()
    # for pair in bad_pairs:
    #     print(repr(pair[0]))
    #     print(repr(pair[1]))
    #     result = difflib.ndiff(pair[0], pair[1])
    #     print(''.join(result))
    #     print()

    # assert len(df[df['Translation АНИСИМОВ'] != df['Русский']]) == 0


if __name__ == '__main__':
    main()
