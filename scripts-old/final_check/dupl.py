import pandas as pd
import os


def main():
    path = '../data/corpus/corpus_final_all_last_dance_new.csv'

    df = pd.read_csv(path)
    df.dropna(subset=['Хакасский'], inplace=True)
    df.dropna(subset=['Русский'], inplace=True)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    print(len(df))
    print(df['Источник'].value_counts())

    sorted_df = df.sort_values(by='Русский', key=lambda x: x.str.len())
    for ist in ['all', 'kjh_rus', 'rus_kjh', 'prince', 'smolsent', 'test_bouquet', 'smoldoc', 'dev_bouquet']:
        df_ist = sorted_df[sorted_df['Источник'] == ist]
        new_path = f'../data/corpus/subcorpus/corpus_final_all_last_dance_sorted_russian_{ist}.csv'
        df_ist.to_csv(new_path, index=False)

    # duplicates = df[df.duplicated(subset='Русский')]
    # print('duplicates "Русский":')
    # print('-' * 10)
    # print(duplicates['Русский'])
    # print('-' * 10)
    # print()


def main2():
    data_dir = '../data/corpus/subcorpus_rus_prepared'
    filenames = sorted(os.listdir(data_dir))
    for filename in filenames:
        if '.xlsx' in filename:
            path = f'{data_dir}/{filename}'
            all_sheets = pd.read_excel(path, sheet_name=None)
            i = 0
            for sheet_name, sheet_df in all_sheets.items():
                i = + 1
                sorted_df = sheet_df.sort_values(by='Хакасский', key=lambda x: x.str.len())
                sorted_df.to_csv(path.replace('.xlsx', f'_{i}_khakas.csv'), index=False)


def main3():
    data_dir = '../data/corpus/corpus_final_all_last_dance_sorted_russian_khakas_prepared'
    pairs = []
    for name in ['smolsent', 'smoldoc', 'dev_bouquet', 'test_bouquet', 'prince', 'kjh_rus', 'rus_kjh', 'all']:
        filename = f'corpus_final_all_last_dance_sorted_russian_{name}_1_khakas.xlsx'
        path = f'{data_dir}/{filename}'
        all_sheets = pd.read_excel(path, sheet_name=None)
        for sheet_name, sheet_df in all_sheets.items():
            pairs.extend(sheet_df[['Русский', 'Хакасский', 'Переводчик', 'Источник']].values.tolist())

    df = pd.DataFrame(pairs, columns=['Русский', 'Хакасский', 'Переводчик', 'Источник'])
    df.dropna(subset=['Хакасский'], inplace=True)
    df.dropna(subset=['Русский'], inplace=True)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    duplicates = df[df.duplicated(subset=["Русский", "Хакасский"])]
    print('rus khak duplicates', len(duplicates))
    print('before', len(df))
    df = df.drop_duplicates(subset=["Русский", "Хакасский"], keep='first')
    print('after', len(df))
    print()

    duplicates = df[df.duplicated(subset="Русский")]
    print('rus duplicates', len(duplicates))
    print('before', len(df))
    df = df.drop_duplicates(subset="Русский", keep='first')
    print('after', len(df))
    print()

    duplicates = df[df.duplicated(subset="Хакасский")]
    print('khak duplicates', len(duplicates))

    print('before', len(df))
    df = df.drop_duplicates(subset="Хакасский", keep='first')
    print('after', len(df))
    print()

    # print('-' * 10)
    # print(duplicates['Хакасский'])
    # print('-' * 10)
    # print()

    df.to_csv('../data/corpus_last_dance/corpus_98835.csv', index=False)



def main4():
    df = pd.read_csv('../data/corpus_last_dance/corpus_100873_added.csv')
    df.dropna(subset=['Хакасский'], inplace=True)
    df.dropna(subset=['Русский'], inplace=True)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    print(len(df))

    duplicates = df[df.duplicated(subset=["Русский", "Хакасский"])]
    print('rus khak duplicates', len(duplicates))
    print('before', len(df))
    df = df.drop_duplicates(subset=["Русский", "Хакасский"], keep='first')
    print('after', len(df))
    print()

    duplicates = df[df.duplicated(subset="Русский")]
    print('rus duplicates', len(duplicates))
    print('before', len(df))
    df = df.drop_duplicates(subset="Русский", keep='first')
    print('after', len(df))
    print()

    duplicates = df[df.duplicated(subset="Хакасский")]
    print('khak duplicates', len(duplicates))

    print('before', len(df))
    df = df.drop_duplicates(subset="Хакасский", keep='first')
    print('after', len(df))
    print()

    # print('-' * 10)
    # print(duplicates['Хакасский'])
    # print('-' * 10)
    # print()

    df.to_csv('../data/corpus_last_dance/corpus_100695_almost_final.csv', index=False)

if __name__ == '__main__':
    import unicodedata
    for symbol in 'абвгдежзийклмнопрстуфхцчшщъыьэюяёіғңҷӧӱ':
        print(symbol, unicodedata.name(symbol))
