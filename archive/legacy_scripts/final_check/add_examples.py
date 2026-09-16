import pandas as pd
from nltk.tokenize import sent_tokenize
import re


def main():
    df = pd.read_csv('../data/corpus_last_dance/corpus_98835.csv')
    df['to_split'] = df.apply(lambda x: x['Переводчик'] in ['Киргинеков Роман Геннадьевич',
                                                            'Чебочакова Ирина Максимовна',
                                                            'Шагдурова Ольга Юрьевна']
                                        and x['Источник'] == 'kjh_rus' and
                                        len(sent_tokenize(x['Русский'], language='russian')) >= 2, axis=1)

    df1 = df[~df['to_split']]
    print(len(df1))
    df1.to_csv('../data/corpus_last_dance/corpus_98835_no_splitted_95866.csv', index=False)

    df2 = df[df['to_split']]
    pairs = []
    pairs1 = df2[['Русский', 'Хакасский', 'Переводчик', 'Источник']].values.tolist()
    for r_sent, k_sent, author, sheet_name in pairs1:
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

    df_new = pd.DataFrame(pairs, columns=['Русский', 'Хакасский', 'Переводчик', 'Источник'])
    df_new = df_new.sort_values(by='Хакасский', key=lambda x: x.str.len())
    print(len(df_new))
    df_new.to_csv('../data/corpus_last_dance/corpus_98835_splitted_2969.csv', index=False)


def main1():
    df = pd.read_csv('../data/corpus_last_dance/corpus_98835_no_splitted_95866.csv')
    df1 = pd.read_csv('../data/corpus_last_dance/corpus_98835_splitted_2969 - checked.csv')
    df3 = pd.concat([df, df1])
    print(len(df3))

    df3.to_csv('../data/corpus_last_dance/corpus_100873_added.csv', index=False)


if __name__ == '__main__':
    main1()
