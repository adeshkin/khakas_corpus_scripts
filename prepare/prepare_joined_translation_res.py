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
            sheet_df['Источник'] = sheet_name
            sheet_df['Исходный язык'] = 'Русский' if any(part in sheet_name for part in ['of my_', 'of spont_com', 'of trun_', 'of averoo_s', 'of gwmt_', 'of common_', 'of coregram', 'of ru_al_']) else 'Хакасский'
            name2fullname = {'of kh_50k_': 'khakaschiry',
                             'of kh_50_': 'khakaschiry',
                 'of uchi_shf_': 'uchebniki_fixed',
                 'of al_': 'khakaschiry_akciya_lydi',
                 'of uchi_': 'uchebniki',
                 'of an_': 'khakaschiry_akciya_nn',
                 'of shch_': 'shulbaeva choohtar',
                 'of my_': 'my examples', 
                 'of spont_com': 'spontaneous common voice interface',
                 'of trun_': 'Trunova',
                 'of averoo_s': 'averoo_sumi_ru_alpaca',
                 'of gwmt_': 'gwmt',
                 'of common_': 'common voice interface',
                 'of coregram': 'coregrammar',
                 'of ru_al_': 'ru_alpaca'}
            sheet_df['Полное название'] = next(
                (fullname for name, fullname in name2fullname.items() if name in sheet_name),
                'unknown',
            )
            sheet_df = sheet_df.dropna(subset=['Русский'])
            sheet_df = sheet_df.dropna(subset=['Хакасский'])
            for column in ['Русский', 'Хакасский']:
                sheet_df[column] = sheet_df[column].astype(str).str.strip()
            
            #sheet_df['no_valid'] = sheet_df.apply(lambda x: min(len(x['Хакасский'].strip()), len(x['Русский'].strip())) < 4 or (not bool(re.search(r'[a-zA-Zа-яА-ЯёЁ]', x['Хакасский']))) or (not bool(re.search(r'[a-zA-Zа-яА-ЯёЁ]', x['Русский']))), axis=1)
            # sheet_df['no_valid'] = sheet_df.apply(
            #                                     lambda x: any(
            #                                         len(x[col].split()) <= 1
            #                                         or sum(char.isalpha() for char in x[col]) <= 5
            #                                         or not re.search(r'[a-zA-Zа-яА-ЯёЁ]', x[col])
            #                                         for col in ('Хакасский', 'Русский')
            #                                     ),
            #                                     axis=1,
            #                                 )
            # sheet_df['no_valid'] = sheet_df.apply(
            #             lambda x: len(x['Хакасский']) * 3 <= len(x['Русский'])
            #             or len(x['Русский']) * 3 <= len(x['Хакасский']) or min(len(x['Хакасский'].strip()), len(x['Русский'].strip())) < 4,
            #             axis=1,
            #         )
            sheet_df['no_valid'] = sheet_df.apply(
                                    lambda x: min(len(x['Хакасский'].strip()), len(x['Русский'].strip())) < 4,
                                    axis=1,
                                )
            if sheet_df['no_valid'].sum() > 0:
                print(sheet_name)
                print(sheet_df[sheet_df['no_valid']][['Хакасский', 'Русский']])
                sheet_df = sheet_df[~sheet_df['no_valid']]

            pairs.extend(sheet_df[['Русский', 'Хакасский', 'Переводчик', 'Источник', 'Исходный язык', 'Полное название']].values.tolist())

            # if sheet_name.startswith('part2_'):
            #     print(sheet_name)
            #     break

        print()
        print(translator)
        print(len(pairs))
        print()
        all_pairs.extend(pairs)

    print('all')
    random.shuffle(all_pairs)
    print(len(all_pairs))
    df = pd.DataFrame(all_pairs, columns=['Русский', 'Хакасский', 'Переводчик', 'Источник', 'Исходный язык', 'Полное название'])
    print(df['Полное название'].value_counts().sort_index())
    print(df['Исходный язык'].value_counts().sort_index())
    print(df['Переводчик'].value_counts().sort_index())
    df.to_csv('/home/adeshkin/Downloads/final_all_2026.csv', index=False)
    for source in df.loc[df['Полное название'] == 'unknown', 'Источник'].unique():
        print(source)



if __name__ == '__main__':
    main()
    #df = pd.read_csv('/home/adeshkin/Downloads/final_2_2026.csv')
    
