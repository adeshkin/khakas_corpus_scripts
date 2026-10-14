import re
import random
import pandas as pd
from glob import glob

def main():
    paths = sorted(glob('/home/adeshkin/Downloads/переводы/*.xlsx'))
    all_pairs = []
    for path in paths:
        all_sheets = pd.read_excel(path, sheet_name=None)
        pairs = []
        translator = path.split('/')[-1].split('-')[0].strip()
        for i, (sheet_name, sheet_df) in enumerate(all_sheets.items()):
            if 'Copy' not in sheet_name:
                print(sheet_name)
                continue
            
            sheet_df.columns = sheet_df.iloc[1]
            sheet_df = sheet_df.iloc[2:]
            sheet_df = sheet_df.reset_index(drop=True)
            sheet_df.columns.name = None

            sheet_df['Переводчик'] = translator
            sheet_df = sheet_df.dropna(subset=['Русский'])
            sheet_df = sheet_df.dropna(subset=['Хакасский'])
            for column in ['Русский', 'Хакасский']:
                sheet_df[column] = sheet_df[column].astype(str).str.strip()
            
            #sheet_df['no_valid'] = sheet_df.apply(lambda x: min(len(x['Хакасский'].strip()), len(x['Русский'].strip())) < 4 or (not bool(re.search(r'[a-zA-Zа-яА-ЯёЁ]', x['Хакасский']))) or (not bool(re.search(r'[a-zA-Zа-яА-ЯёЁ]', x['Русский']))), axis=1)
            sheet_df['no_valid'] = sheet_df.apply(
                                                lambda x: any(
                                                    len(x[col].split()) <= 1
                                                    or sum(char.isalpha() for char in x[col]) <= 5
                                                    or not re.search(r'[a-zA-Zа-яА-ЯёЁ]', x[col])
                                                    for col in ('Хакасский', 'Русский')
                                                ),
                                                axis=1,
                                            )
            if sheet_df['no_valid'].sum() > 0:
                print(sheet_name)
                print(sheet_df[sheet_df['no_valid']])
                sheet_df = sheet_df[~sheet_df['no_valid']]

            pairs.extend(sheet_df[['Русский', 'Хакасский', 'Переводчик']].values.tolist())

            if sheet_name.startswith('part2_'):
                print(sheet_name)
                break

        print()
        print(translator)
        print(len(pairs))
        print()
        all_pairs.extend(pairs)

    print('all')
    random.shuffle(all_pairs)
    print(len(all_pairs))
    df = pd.DataFrame(all_pairs, columns=['Русский', 'Хакасский', 'Переводчик'])
    df.to_csv('/home/adeshkin/Downloads/final_2_2026.csv', index=False)



if __name__ == '__main__':
    # main()
    df = pd.read_csv('/home/adeshkin/Downloads/final_2_2026.csv')
    print(df['Переводчик'].value_counts().sort_index())
