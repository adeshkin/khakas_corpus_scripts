import pandas as pd
import re
import os

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)


def main():
    path = '/home/adeshkin/Desktop/проект по переводу хакниияли 2025-20251129T120238Z-1-001/проект по переводу хакниияли 2025/ВЫЧИТКА ПЕРЕВОДОВ/англ-рус от яндекса 1.3/отредактированные/vse_part1_part2_[_(_kulumaeva_13_chelovek.xlsx'

    all_sheets1 = pd.read_excel(path, sheet_name=None)
    for sheet_name, sheet_df in all_sheets1.items():
        sheet_df['Переводчик'] = None
        sheet_df['Источник'] = 'all'

        print(len(sheet_df))
        sheet_df.dropna(subset=['Хакасский (Редактор)'], inplace=True)
        sheet_df.dropna(subset=['Русский'], inplace=True)
        sheet_df = sheet_df.map(lambda x: x.strip() if isinstance(x, str) else x)
        print(len(sheet_df))

        sheet_df['not_valid'] = sheet_df.apply(lambda x: (not re.search(r'[А-Яа-яІіҒғҢңҶҷӦӧӰӱ]',
                                                                        str(x['Хакасский (Редактор)']))), axis=1)

        # print(sheet_df[sheet_df['not_valid']][['Русский', 'Хакасский (Редактор)']])
        sheet_df = sheet_df[~sheet_df['not_valid']]
        print(len(sheet_df))

        sheet_df['not_valid'] = sheet_df.apply(lambda x: (not re.search(r'[А-Яа-я]',
                                                                        str(x['Русский']))), axis=1)
        # print('not valid russian')
        # print(sheet_df[sheet_df['not_valid']][['Русский', 'Хакасский (Редактор)']])
        sheet_df = sheet_df[~sheet_df['not_valid']]
        print(len(sheet_df))

        # sheet_df['not_valid'] = sheet_df.apply(lambda x: len(x['Хакасский (Редактор)']) < 11, axis=1)
        # print()
        # # print('not valid len')
        # # print(sheet_df[sheet_df['not_valid']][['Русский', 'Хакасский (Редактор)']])
        # sheet_df = sheet_df[~sheet_df['not_valid']]
        # print(len(sheet_df))

        duplicates = sheet_df[sheet_df.duplicated(subset='Русский')]
        # print('duplicates "Русский":')
        # print('-' * 10)
        # print(duplicates['Русский'])
        # print('-' * 10)
        # print()
        sheet_df = sheet_df.drop_duplicates(subset='Русский')
        print('dupl rus', len(sheet_df))

        duplicates = sheet_df[sheet_df.duplicated(subset='Хакасский (Редактор)')]
        # print('duplicates "Хакасский (Редактор)":')
        # print('-' * 10)
        # print(duplicates['Хакасский (Редактор)'])
        # print('-' * 10)
        # print()
        sheet_df = sheet_df.drop_duplicates(subset='Хакасский (Редактор)')
        print('dupl khak', len(sheet_df))
        sheet_df.to_csv(path.replace('.xlsx', '_clean_final_new.csv'), index=False)
        sorted_df = sheet_df.sort_values(by='Русский', key=lambda x: x.str.len())
        sorted_df.to_csv(path.replace('.xlsx', '_clean_sorted_russian.csv'), index=False)
        sorted_df = sheet_df.sort_values(by='Хакасский (Редактор)', key=lambda x: x.str.len())
        sorted_df.to_csv(path.replace('.xlsx', '_clean_sorted_khakas.csv'), index=False)
        # \(\)
        # \[\]
        # sheet_df['khakas_with_('] = sheet_df.apply(lambda x: bool(re.search(r'[\(\)]', x['Русский']))
        #                                     and (not bool(re.search(r'[\(\)]', x['Хакасский (Редактор)']))), axis=1)
        # df1 = sheet_df[sheet_df['khakas_with_(']]
        # df1.to_csv(path.replace('.xlsx', '_clean_rus_with_(.csv'), index=False)


def main1():
    data_dir = '/home/adeshkin/Desktop/проект по переводу хакниияли 2025-20251129T120238Z-1-001/проект по переводу хакниияли 2025/ПЕРЕВОДЫ/копии'
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

    df['not_valid'] = df.apply(lambda x: (not re.search(r'[А-Яа-яІіҒғҢңҶҷӦӧӰӱ]', str(x['Хакасский']))), axis=1)
    # print(df[df['not_valid']][['Русский', 'Хакасский']])
    print(len(df))
    df = df[~df['not_valid']]
    print(len(df))

    df['not_valid'] = df.apply(lambda x: (not re.search(r'[А-Яа-я]', str(x['Русский']))), axis=1)
    print('not valid russian')
    # print(df[df['not_valid']][['Хакасский', 'Переводчик']])
    print(len(df))
    df = df[~df['not_valid']]
    print(len(df))

    df['len_kjh'] = df.apply(lambda x: len(re.findall(r'\b\w{2,}\b', x['Хакасский'])), axis=1)
    df['len_rus'] = df.apply(lambda x: len(re.findall(r'\b\w{2,}\b', x['Русский'])), axis=1)

    df['not_valid'] = df.apply(lambda x: x['len_kjh'] < 2 and x['len_rus'] > 4, axis=1)
    #print(df[df['not_valid']][['Русский', 'Хакасский']])
    print(len(df))
    df = df[~df['not_valid']]
    print(len(df))
    print()

    df['not_valid'] = df.apply(lambda x: x['len_rus'] < 3 and x['Источник'] == 'all', axis=1)
    print(df[df['not_valid']][['Хакасский', 'Переводчик']])
    print(len(df))
    df = df[~df['not_valid']]
    print(len(df))
    print()

    # df['not_valid'] = df.apply(lambda x: len(x['Хакасский']) < 2, axis=1)
    # print('not valid len')
    # print(df[df['not_valid']][['Хакасский', 'Переводчик']])
    # print(len(df))
    # df = df[~df['not_valid']]
    # print(len(df))
    #
    # df['not_valid'] = df.apply(lambda x: len(x['Русский']) < 2, axis=1)
    # print('not valid len')
    # print(df[df['not_valid']][['Русский', 'Переводчик']])
    # print(len(df))
    # df = df[~df['not_valid']]
    # print(len(df))


if __name__ == '__main__':
    main()
