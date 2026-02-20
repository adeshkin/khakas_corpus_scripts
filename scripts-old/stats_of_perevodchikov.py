import pandas as pd
import re

def main():
    path = 'data/part1/prepare_for_redaktors_all.csv'
    df = pd.read_csv(path)
    print(df['Переводчик'].unique())

def main2():
    path = 'data/corpus_final.csv'
    df = pd.read_csv(path)
    df['Источник'] = df['Источник'].apply(lambda x: x if x in ['all', 'rus_kjh', 'kjh_rus'] else 'rus_kjh_dataset')
    df['Длинное предложение'] = df['Русский'].apply(lambda x: len(re.findall(r'\b\w{2,}\b', x)) >= 9)
    df['Источник'] = df.apply(lambda x: 'all_long' if x['Источник'] == 'all' and x['Длинное предложение'] else x['Источник'], axis=1)

    df1 = df[['Переводчик', 'Источник']].value_counts().rename_axis(['Переводчик', 'Источник']).reset_index(name='Число предложений')
    result_df = df1.pivot_table(index='Переводчик', columns='Источник', values='Число предложений')

    result_df.columns.name = None
    result_df.reset_index(inplace=True)

    for col in ['all', 'all_long', 'rus_kjh', 'kjh_rus', 'rus_kjh_dataset']:
        result_df[col] = result_df[col].apply(lambda x: x if not pd.isna(x) else 0)

    result_df['all'] = result_df['all'].astype(int)
    result_df['all_long'] = result_df['all_long'].astype(int)
    result_df['rus_kjh'] = result_df['rus_kjh'].astype(int)
    result_df['kjh_rus'] = result_df['kjh_rus'].astype(int)
    result_df['rus_kjh_dataset'] = result_df['rus_kjh_dataset'].astype(int)
    print(len(result_df))

    result_df.to_csv('data/Финальный отчет - Лист1-done.csv', index=False)


def main1():
    path = 'data/corpus_final.csv'
    df = pd.read_csv(path)

    print(df[df['Русский'] == 'Как минимум, страны должны представлять информацию об активности гриппа.']['Переводчик'])
    # print(len(df))
    # print(df['Переводчик'].value_counts())
    # print(len(df['Переводчик'].value_counts()))



if __name__ == '__main__':
    main1()