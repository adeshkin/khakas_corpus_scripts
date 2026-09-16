import pandas as pd
import os

pd.set_option('display.max_colwidth', None)


def check(df, df_1):
    mask1 = df["Хакасский"].isin(df_1["Хакасский"])
    mask1_rus = df["Русский"].isin(df_1["Русский"])
    mask1_df1 = mask1 | mask1_rus
    df = df[~mask1_df1]

    return df

def read_key_datasets():
    data_dir = '../data/key_datasets'
    filenames = os.listdir(data_dir)
    pairs = []
    for filename in filenames:
        path = f'{data_dir}/{filename}'
        df = pd.read_csv(path)
        df['Переводчик'] = None
        df['Источник'] = filename.split('-')[0].strip()
        pairs.extend(df[['Русский', 'Хакасский (Редактор)', 'Переводчик', 'Источник']].values.tolist())

    return pairs


def main():
    data_dir = '/home/adeshkin/Desktop/проект по переводу хакниияли 2025-20251129T120238Z-1-001/проект по переводу хакниияли 2025/ПЕРЕВОДЫ/копии'
    filenames = sorted(os.listdir(data_dir))

    path = '/home/adeshkin/Desktop/проект по переводу хакниияли 2025-20251129T120238Z-1-001/проект по переводу хакниияли 2025/ВЫЧИТКА ПЕРЕВОДОВ/англ-рус от яндекса 1.3/отредактированные/vse_part1_part2_[_(_kulumaeva_13_chelovek_clean_final.csv'


    pairs = []

    df_red = pd.read_csv(path)
    df_red = df_red.map(lambda x: x.strip() if isinstance(x, str) else x)

    df_1 = pd.read_csv('../data/sentences_with_(.csv')
    df_1.dropna(subset=['Хакасский'], inplace=True)
    df_1.dropna(subset=['Русский'], inplace=True)
    df_2 = pd.read_csv('../data/sentences_with_[.csv')


    for filename in filenames:
        path = f'{data_dir}/{filename}'
        author = filename.split('Копия')[1].split('норм')[0].strip()
        all_sheets = pd.read_excel(path, sheet_name=None)
        for sheet_name, sheet_df in all_sheets.items():
            sheet_df['Переводчик'] = author
            sheet_df['Источник'] = sheet_name
            pairs.extend(sheet_df[['Русский', 'Хакасский', 'Переводчик', 'Источник']].values.tolist())
    pairs.extend(read_key_datasets())
    df = pd.DataFrame(pairs, columns=['Русский', 'Хакасский', 'Переводчик', 'Источник'])
    df.dropna(subset=['Хакасский'], inplace=True)
    df.dropna(subset=['Русский'], inplace=True)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    print('before', len(df))
    df_1_rest = check(df_1, df)
    df = check(df, df_1)
    print('after', len(df))

    print(len(df_1_rest), len(df_1))

    print('before', len(df))
    df_2_rest = check(df_2, df)
    df = check(df, df_2)
    print('after', len(df))
    print(len(df_2_rest), len(df_2))

    df.to_csv('../data/join_corpus_brackets.csv', index=False)
    df_1_rest = df_1_rest.sort_values(by='Хакасский', key=lambda x: x.str.len())
    df_1_rest.to_csv('../data/join_corpus_brackets_df1_rest.csv', index=False)
    df_2_rest = df_2_rest.sort_values(by='Хакасский', key=lambda x: x.str.len())
    df_2_rest.to_csv('../data/join_corpus_brackets_df2_rest.csv', index=False)


    # df['not_valid'] = df.apply(lambda x: (not re.search(r'[А-Яа-яІіҒғҢңҶҷӦӧӰӱ]', str(x['Хакасский (Редактор)']))), axis=1)
    # print(df[df['not_valid']][['Русский', 'Хакасский (Редактор)']])
    # df = df[~df['not_valid']]
    #
    # print(len(df))
    # duplicates = df[df.duplicated(subset='Русский')]
    # print('duplicates "Русский":')
    # print(duplicates['Русский'])
    # print('-' * 10)
    # print(len(duplicates))
    #
    # print('-' * 10)
    # print()
    # df = df.drop_duplicates(subset='Русский', keep='first')


    #df.to_csv('../data/join_corpus.csv', index=False)






if __name__ == '__main__':
    main()
