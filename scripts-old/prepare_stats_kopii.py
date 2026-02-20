import pandas as pd
import os
import re
import nltk
nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize
pd.set_option('display.max_colwidth', None)


def main():
    data_dir = '/home/adeshkin/Desktop/ПЕРЕВОДЫ-20251120T132738Z-1-001/ПЕРЕВОДЫ/копии'
    filenames = sorted(os.listdir(data_dir))
    pairs = []
    for filename in filenames:
        path = f'{data_dir}/{filename}'
        author = filename.split('Копия')[1].split('.xlsx')[0].strip()
        print(filename)
        print('-'*10)
        all_sheets = pd.read_excel(path, sheet_name=None)
        for sheet_name, sheet_df in all_sheets.items():
            sheet_df['Переводчик'] = author
            sheet_df['Источник'] = sheet_name
            print(sheet_name)
            if sheet_name == 'kjh_rus':
                if author in [
                              'Абумова Ольга Дмитриевна',
                              'Киргинеков Роман Геннадьевич',
                              'Кичеева Кристина Владимировна',
                              'Кызласова Инга Людовиковна',
                              'Мамышев Игорь Филиппович',
                              'Субракова Вия Васильевна',
                              'Чебочакова Ирина Максимовна',
                              'Шагдурова Ольга Юрьевна']:
                    sheet_df.dropna(subset=['Хакасский'], inplace=True)
                    sheet_df.dropna(subset=['Русский'], inplace=True)
                    pairs1 = sheet_df[['Русский', 'Хакасский']].values.tolist()
                    for r_sent, k_sent in pairs1:
                        r_splitted = sent_tokenize(r_sent, language='russian')
                        k_splitted = sent_tokenize(k_sent, language='russian')
                        if len(r_splitted) > 1 and len(r_splitted) == len(k_splitted):
                            r_join_sent = ''
                            k_join_sent = ''
                            for r_example, k_example in zip(r_splitted, k_splitted):
                                r_join_sent = r_join_sent + ' ' + r_example
                                k_join_sent = k_join_sent + ' ' + k_example
                                len_sent = len(re.findall(r'\b[А-Яа-яІіҒғҢңҶҷӦӧӰӱ]{2,}\b', r_join_sent))
                                if len_sent > 4:
                                    pairs.append((r_join_sent.strip(), k_join_sent.strip(), author, sheet_name))
                                    r_join_sent = ''
                                    k_join_sent = ''

                            if r_join_sent != '':
                                pairs.append((r_join_sent.strip(), k_join_sent.strip(), author, sheet_name))
                        else:
                            pairs.append((r_sent.strip(), k_sent.strip(), author, sheet_name))
                else:
                    pairs.extend(sheet_df[['Русский', 'Хакасский', 'Переводчик', 'Источник']].values.tolist())

            else:

                pairs.extend(sheet_df[['Русский', 'Хакасский', 'Переводчик', 'Источник']].values.tolist())
        print()
    print(len(pairs))
    df = pd.DataFrame(pairs, columns=['Русский', 'Хакасский', 'Переводчик', 'Источник'])
    df.dropna(subset=['Хакасский'], inplace=True)
    df.dropna(subset=['Русский'], inplace=True)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    print(len(df))
    df['not_valid'] = df.apply(lambda x: len(str(x['Хакасский'])) < 4 or (not re.search(r'[А-Яа-яІіҒғҢңҶҷӦӧӰӱ]', str(x['Хакасский']))) or (not re.search(r'[А-Яа-я]', str(x['Русский']))), axis=1)

    df1 = df[df['not_valid']]
    df2 = df[~df['not_valid']]
    print()
    print()
    print(len(df2))

    df2.to_csv('data/corpus_final.csv', index=False)
    df1.to_csv('data/corpus_final_not_valid.csv', index=False)


if __name__ == '__main__':
    main()
