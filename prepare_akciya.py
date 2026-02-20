import pandas as pd


def main():
    path = '/home/adeshkin/Downloads/akciy_23_11_23_obuchaem_neuroset_khakas-20260219T044158Z-1-001/akciy_23_11_23_obuchaem_neuroset_khakas/Школа Бутрахты.xlsx'
    xls = pd.ExcelFile(path)
    sheet_names = xls.sheet_names
    kjh_sents = []
    pairs = []
    for sheet in sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        kjh_sents = df['Хакасский'].values.tolist()
        # kjh_sents.extend(df['Хакасский'].values.tolist())
        df.dropna(axis=0, how='any', inplace=True)
        pairs.extend(df[['Хакасский', 'Русский']].values.tolist())


    kjh_sents = list(set(kjh_sents))
    df = pd.DataFrame(pairs, columns=['Хакасский', 'Русский'])
    df = df.sort_values(by='Русский', key=lambda x: x.str.len())
    print(df.head())
    df.drop_duplicates(inplace=True, keep='first')
    df.drop_duplicates(subset='Хакасский', inplace=True, keep='first')
    df.drop_duplicates(subset='Русский', inplace=True, keep='first')
    kjh_sents_translated = df['Хакасский'].values.tolist()

    kjh_left = set(kjh_sents).difference(set(kjh_sents_translated))
    print(len(kjh_left))
    print(len(kjh_sents_translated))
    df.to_csv('/home/adeshkin/Downloads/Школа Бутрахты - проверить.csv', index=False)

    df = pd.DataFrame(kjh_left, columns=['Хакасский'])
    df.drop_duplicates(inplace=True)
    df.to_csv('/home/adeshkin/Downloads/Школа Бутрахты - перевести.csv', index=False)



if __name__ == '__main__':
    main()