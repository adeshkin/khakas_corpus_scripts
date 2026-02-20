import os
import pandas as pd

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
    df_1 = pd.read_csv('../data/sentences_with_(.csv')
    df_1.dropna(subset=['Хакасский'], inplace=True)
    df_1.dropna(subset=['Русский'], inplace=True)
    df_2 = pd.read_csv('../data/sentences_with_[.csv')
    df_2.dropna(subset=['Хакасский'], inplace=True)
    df_2.dropna(subset=['Русский'], inplace=True)

    data_dir = '/home/adeshkin/Desktop/проект по переводу хакниияли 2025-20251130T092542Z-1-001/проект по переводу хакниияли 2025/ПЕРЕВОДЫ/копии'
    filenames = sorted(os.listdir(data_dir))
    pairs = []
    for filename in filenames:
        path = f'{data_dir}/{filename}'
        author = filename.split('Копия')[1].split('норм')[0].strip()
        all_sheets = pd.read_excel(path, sheet_name=None)
        for sheet_name, sheet_df in all_sheets.items():
            sheet_df['Переводчик'] = author
            sheet_df['Источник'] = sheet_name
            pairs.extend(sheet_df[['Русский', 'Хакасский', 'Переводчик', 'Источник']].values.tolist())

    df = pd.DataFrame(pairs, columns=['Русский', 'Хакасский', 'Переводчик', 'Источник'])
    df.dropna(subset=['Хакасский'], inplace=True)
    df.dropna(subset=['Русский'], inplace=True)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    print(df['Источник'].value_counts())

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

    df_red = pd.read_csv('../data/corpus/vse_part1_part2_[_(_kulumaeva_13_chelovek_clean_final_new.csv')
    df_red.dropna(subset=['Хакасский (Редактор)'], inplace=True)
    df_red.dropna(subset=['Русский'], inplace=True)
    df_red = df_red.map(lambda x: x.strip() if isinstance(x, str) else x)
    pairs_new = read_key_datasets()
    pairs_new.extend(df_red[['Русский', 'Хакасский (Редактор)', 'Переводчик', 'Источник']].values.tolist())
    pairs_new.extend(df[['Русский', 'Хакасский', 'Переводчик', 'Источник']].values.tolist())
    df_new = pd.DataFrame(pairs_new, columns=['Русский', 'Хакасский', 'Переводчик', 'Источник'])
    df_new.to_csv('../data/corpus/corpus_final_all_last_dance_new.csv', index=False)
    print(len(df_new))


if __name__ == "__main__":
    main()
