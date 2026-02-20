import pandas as pd
import re
from pymorphy3 import MorphAnalyzer

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

morph = MorphAnalyzer()

def get_normal_form(word):
    p = morph.parse(word)[0]

    return p.normal_form


def find_in_dict(x, df_dict, col='semgloss'):
    result = df_dict[df_dict[col] == x]['word'].tolist()
    if len(result) == 0:
        return None
    return result


def dict_contains(x, df_dict, col='field1'):
    result = df_dict[df_dict[col].notnull() & df_dict[col].str.contains(x)][col].values.tolist()
    result = [re.findall(r'.{1,30}' + re.escape(x) + r'.{1,30}', y) for y in result]
    if len(result) == 0:
        return None
    return result


def exact_match():
    df_dict = pd.read_csv('/home/adeshkin/Desktop/gatitos/hrs_new34_clean_4_col.csv')
    for col in ['semgloss']:
        df_dict[col] = df_dict[col].apply(lambda x: str(x).strip().lower())

    df = pd.read_excel('/home/adeshkin/Desktop/gatitos/gatitos_russian_by_yandex_translator.xlsx', header=None)
    df_en = pd.read_excel('/home/adeshkin/Desktop/gatitos/gatitos_english.xlsx', header=None)

    df['Английский'] = df_en[0]
    df.rename(columns={0: 'Русский'}, inplace=True)
    df['Хакасский'] = df['Русский'].apply(lambda x: find_in_dict(str(x).strip().lower(), df_dict))

    print(df['Хакасский'].isna().sum())
    print(len(df))
    print(df['Хакасский'].isna().sum() / len(df))
    print()
    print(df.head())

    df.to_csv('/home/adeshkin/Desktop/gatitos/gatitos_khakas_exact_match_hrs_new34_clean_4_col.csv', index=False)


def exact_match_normal_form():
    df_dict = pd.read_csv('/home/adeshkin/Desktop/gatitos/hrs_new34_clean_4_col.csv')
    df = pd.read_csv('/home/adeshkin/Desktop/gatitos/gatitos_khakas_exact_match_hrs_new34_clean_4_col.csv')
    df.fillna(value=pd.NA, inplace=True)

    for col in ['semgloss']:
        df_dict[col] = df_dict[col].apply(lambda x: str(x).strip().lower())

    df['Русский_normal_form'] = df['Русский'].apply(lambda x: get_normal_form(str(x).strip().lower()))

    df['Хакасский_normal_form'] = df['Русский_normal_form'].apply(lambda x: find_in_dict(str(x), df_dict))

    print(df['Хакасский_normal_form'].notna().sum())
    print(len(df))
    print(df['Хакасский_normal_form'].notna().sum() / len(df))
    print()

    df.to_csv('/home/adeshkin/Desktop/gatitos/gatitos_khakas_exact_match_normal_form_hrs_new34_clean_4_col.csv', index=False)


def field1_match():
    df_dict = pd.read_csv('/home/adeshkin/Desktop/gatitos/hrs_new34_clean_4_col.csv')
    df = pd.read_csv('/home/adeshkin/Desktop/gatitos/gatitos_khakas_exact_match_hrs_new34_clean_4_col.csv')
    df.fillna(value=pd.NA, inplace=True)

    for col in ['field1']:
        df_dict[col] = df_dict[col].apply(lambda x: str(x).strip().lower())

    df['Хакасский_field1'] = df.apply(lambda x:
                                      dict_contains(str(x['Русский']).strip().lower(), df_dict, 'field1')
                                      if x['Хакасский'].isna() else x['Хакасский'], axis=1)

    print(df['Хакасский_field1'].notna().sum())
    print(len(df))
    print(df['Хакасский_field1'].notna().sum() / len(df))
    print()

    print(df.sample(10))


if __name__ == '__main__':
    exact_match_normal_form()
