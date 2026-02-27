import pandas as pd


def main():
    path = '/home/adeshkin/khakas_projects/data/translation/e_corpus/электронный корпус хакасского языка.xlsx'
    all_sheets = pd.read_excel(path, sheet_name=None)
    pairs = []
    for sheet_name, sheet_df in all_sheets.items():
        sheet_df['Источник'] = sheet_name
        pairs.extend(sheet_df[['Русский', 'Хакасский', 'Источник']].values.tolist())

    path = '/home/adeshkin/khakas_projects/data/translation/e_corpus/электронный корпус хакасского языка - библия.xlsx'
    all_sheets = pd.read_excel(path, sheet_name=None)
    for sheet_name, sheet_df in all_sheets.items():
        sheet_df['Источник'] = sheet_name
        pairs.extend(sheet_df[['Русский', 'Хакасский', 'Источник']].values.tolist())

    path = '/home/adeshkin/khakas_projects/data/translation/e_corpus/электронный корпус хакасского языка - фольклор.xlsx'
    all_sheets = pd.read_excel(path, sheet_name=None)
    for sheet_name, sheet_df in all_sheets.items():
        sheet_df['Источник'] = sheet_name
        pairs.extend(sheet_df[['Русский', 'Хакасский', 'Источник']].values.tolist())

    df = pd.DataFrame(pairs, columns=['Русский', 'Хакасский', 'Источник'])
    print(len(df))
    df = df.drop(df[(df['Русский'].isna()) | (len(df['Русский']) < 3)].index)
    print(len(df))
    df = df.drop(df[(df['Хакасский'].isna()) | (len(df['Хакасский']) < 3)].index)
    print(len(df))
    df.to_csv('/home/adeshkin/khakas_projects/data/translation/e_corpus/e_corpus.csv', index=False)


if __name__ == '__main__':
    main()
