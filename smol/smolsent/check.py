import pandas as pd
import re
import difflib

pd.set_option('display.max_colwidth', None)


def main():
    df1 = pd.read_csv('/home/adeshkin/Downloads/smolsent.csv')
    df1 = df1.fillna('')

    df2 = pd.read_csv('/home/adeshkin/Downloads/Чебочакова Ирина Максимовна - 2026 - Copy of smolsent_fix.csv')
    df2 = df2.fillna('')

    df2['Translation АНИСИМОВ'] = df2['Русский (Новый)']

    df = pd.read_csv('/home/adeshkin/Downloads/Чебочакова Ирина Максимовна - 2026 - Copy of smolsent.csv')
    df = df.fillna('')

    # print(len(df))
    # print(len(df2))

    assert len(df) == len(df1)
    df['Translation АНИСИМОВ'] = df1['Translation АНИСИМОВ']
    df['Translation АНИСИМОВ'] = df['Translation АНИСИМОВ'].apply(lambda x: x.strip())
    df['Русский'] = df['Русский'].apply(lambda x: x.strip())
    df1 = df[df['Translation АНИСИМОВ'] != df['Русский']]

    # print(len(df1))

    mapping = df2.set_index('Translation АНИСИМОВ')['Хакасский (Новый)']

    df1['kjh_new'] = df1['Translation АНИСИМОВ'].map(mapping).fillna('')
    df1.loc[df1[
                'Translation АНИСИМОВ'] == '– О нет! Все в порядке? – обеспокоенно ответила Латаша.', 'kjh_new'] = '– Йу, чох! Прай ниме чахсы ба? - сағыссырап нандырған Латаша.'
    df1.loc[df1[
                'Translation АНИСИМОВ'] == 'Адаптивность — гибкий быстрый ум, оптимистичный настрой;', 'kjh_new'] = 'Кӧнігіс – чітіг табырах сағыс, оптимистичнай оңдай;'
    df1.loc[df1[
                'Translation АНИСИМОВ'] == 'Во-вторых, официальный знак одобрения  — это поцелуй смерти для любой по-настоящему вирусной кампании.', 'kjh_new'] = 'Ікінҷізін, официальнай чарадығ тании – ол хайдағ даа сын вирустығ кампанияа ӧлімнің охсанызы.'

    print(len(df2))
    print(len(df1[df1['kjh_new'] != '']))

    mapping = df1.set_index('Translation АНИСИМОВ')['kjh_new']
    df['kjh_new'] = df['Translation АНИСИМОВ'].map(mapping).fillna('')
    print(len(df[df['kjh_new'] == '']))
    df['kjh_final'] = df.apply(lambda x: x['Хакасский (Редактор)'] if x['kjh_new'] == '' else x['kjh_new'], axis=1)
    print(len(df[df['kjh_final'] == '']))
    print(len(df[df['kjh_final'] != '']))

    df3 = pd.read_csv('/home/adeshkin/Downloads/smolsent.csv')
    df3 = df3.fillna('')
    mapping = df.set_index('Translation АНИСИМОВ')['kjh_final']
    df3['kjh'] = df['Translation АНИСИМОВ'].map(mapping).fillna('')
    print(len(df3[df3['kjh'] == '']))

    df3.to_csv('/home/adeshkin/Downloads/smolsent_final.csv')
    # # print(len(df1))
    # # diff_df1 = df1[~df1['Translation АНИСИМОВ'].isin(df2['Русский (Новый)'])]
    # diff_df2 = df2[~df2['Русский (Новый)'].isin(df1['Translation АНИСИМОВ'])]
    # print(len(diff_df2))
    # print(diff_df1['Translation АНИСИМОВ'])
    # bad_pairs = df1[df1['kjh_new'] == ''][['Translation АНИСИМОВ', 'Русский']].values.tolist()
    # print(len(bad_pairs))
    # for pair in bad_pairs:
    #     print(repr(pair[0]))
    #     print(repr(pair[1]))
    #     result = difflib.ndiff(pair[0], pair[1])
    #     print(''.join(result))
    #     print()

    # print(df[df['en'] != df['en_orig']][['en', 'en_orig']].head())
    # assert len(df[df['en'] != df['en_orig']]) == 0

    # df['ru_orig'] = df['Translation АНИСИМОВ'].apply(lambda x: re.sub(r'\W', '', x))
    # df['ru_our'] = df['Русский'].apply(lambda x: re.sub(r'\W', '', x))

    # bad_pairs = df1[df1['ru_orig'] != df1['ru_our']][['Translation АНИСИМОВ', 'Русский']].values.tolist()
    # print(len(bad_pairs))
    # for pair in bad_pairs:
    #     print(pair[0])
    #     result = difflib.ndiff(pair[0], pair[1])
    #     print(''.join(result))
    #     print()
    #
    # df1 = df[df['ru_orig'] != df['ru_our']]
    # df1.to_csv('/home/adeshkin/Downloads/smolsent_kjh_all - Sheet1 (2)_to_fix.csv')
    # print(len(df1))

    # assert len(df[df['Translation АНИСИМОВ'] != df['Русский']]) == 0


def main2():
    df = pd.read_csv('/home/adeshkin/Downloads/smolsent_final.csv')
    df = df.fillna('')

    df1 = pd.read_csv('/home/adeshkin/Downloads/smolsent.csv')
    df1 = df1.fillna('')
    assert len(df) == len(df1)
    print(len(df[df['en'] != df1['en']]))
    print(len(df[df['Translation АНИСИМОВ'] != df1['Translation АНИСИМОВ']]))

    df2 = pd.read_csv('/home/adeshkin/Downloads/Чебочакова Ирина Максимовна - 2026 - Copy of smolsent_fix.csv')
    df2 = df2.fillna('')
    print(len(df2[df2['Хакасский (Новый)'] != df2['Хакасский']]))
    kjh_sents2 = df2[df2['Хакасский (Новый)'] != df2['Хакасский']]['Хакасский (Новый)'].values.tolist()
    bad_pairs = df2[df2['Хакасский (Новый)'] == df2['Хакасский']][['Русский (Новый)', 'Русский']].values.tolist()
    print(len(bad_pairs))
    for pair in bad_pairs:
        print(pair[0])
        print(pair[1])
        print()
        # result = difflib.ndiff(pair[0], pair[1])
        # print(''.join(result))
        # print()

    df2['Translation АНИСИМОВ'] = df2['Русский (Новый)'].apply(lambda x: x.strip())
    df['Translation АНИСИМОВ'] = df['Translation АНИСИМОВ'].apply(lambda x: x.strip())
    ru_sents = df['Translation АНИСИМОВ'].tolist()
    ru_sents2 = df2['Translation АНИСИМОВ'].tolist()
    # print(len(df2))
    # print(len(df[df['ru'] != '']))
    #print(df[df['ru'] == '']['Translation АНИСИМОВ'])

    # df3 = pd.read_csv('/home/adeshkin/Downloads/Чебочакова Ирина Максимовна - 2026 - Copy of smolsent.csv')
    # df3 = df3.fillna('')
    # assert len(df) == len(df3)
    # print(len(df[df['kjh'] != df3['Хакасский (Редактор)']]))
    # kjh_sents = df[df['kjh'] != df3['Хакасский (Редактор)']]['kjh'].values.tolist()
    examples = [x for x in ru_sents2 if x not in ru_sents]
    # examples  = [x for x in ru_sents2 if x not in kjh_sents]
    print(len(examples))
    print(examples)




if __name__ == '__main__':
    main2()
