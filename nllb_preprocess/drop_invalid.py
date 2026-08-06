import os

import pandas as pd


def drop_v1():
    path = '../data/khakas_russian_parallel_corpus_v1_fix_symbols.csv'
    save_path = '../data/khakas_russian_parallel_corpus_v1_fix_symbols_drop.csv'
    assert not os.path.exists(save_path)

    df = pd.read_csv(path)
    print(len(df))

    df = df.dropna(subset=['Русский'])
    print(len(df))

    df = df.dropna(subset=['Хакасский'])
    print(len(df))

    df = df.drop(df[df['Источник'] == 'Хакасско-русский словарь'].index)
    print(len(df))

    excluded_sources = ['smolsent', 'smoldoc', 'dev_bouquet', 'test_bouquet']
    df = df[~df['Источник'].isin(excluded_sources)]
    print(len(df))

    s

    df.to_csv(save_path, index=False)


def drop_ec():
    path = '../data/e_corpus_fix_symbols.csv'
    save_path = '../data/e_corpus_fix_symbols_drop.csv'
    assert not os.path.exists(save_path)

    df = pd.read_csv(path)
    print(len(df))

    df = df.dropna(subset=['Русский'])
    print(len(df))

    df = df.dropna(subset=['Хакасский'])
    print(len(df))

    df = df[df['Русский'].str.count('\\w+') >= 2]
    print(len(df))

    df = df[df['Хакасский'].str.count('\\w+') >= 2]
    print(len(df))

    df.to_csv(save_path, index=False)


def drop_til():
    path = '../data/til_para_corpus_fix_symbols.csv'
    save_path = '../data/til_para_corpus_fix_symbols_drop.csv'
    assert not os.path.exists(save_path)

    df = pd.read_csv(path)
    print(len(df))

    df = df.dropna(subset=['Русский'])
    print(len(df))

    df = df.dropna(subset=['Хакасский'])
    print(len(df))

    df = df[df['Русский'].str.count('\\w+') >= 2]
    print(len(df))

    df = df[df['Хакасский'].str.count('\\w+') >= 2]
    print(len(df))

    df.to_csv(save_path, index=False)


def drop_vl():
    path = '../data/vkloc_fix_symbols.csv'
    save_path = '../data/vkloc_fix_symbols_drop.csv'
    assert not os.path.exists(save_path)

    df = pd.read_csv(path)
    print(len(df))

    df = df.dropna(subset=['Русский'])
    print(len(df))

    df = df.dropna(subset=['Хакасский'])
    print(len(df))

    df = df[df['Русский'].str.count('\\w+') >= 2]
    print(len(df))

    df = df[df['Хакасский'].str.count('\\w+') >= 2]
    print(len(df))

    df.to_csv(save_path, index=False)


def drop_klr():
    path = '../data/klr_fix_symbols.csv'
    save_path = '../data/klr_fix_symbols_drop.csv'
    assert not os.path.exists(save_path)

    df = pd.read_csv(path)
    print(len(df))

    df = df.dropna(subset=['Русский'])
    print(len(df))

    df = df.dropna(subset=['Хакасский'])
    print(len(df))

    df = df[df['Русский'].str.count('\\w+') >= 5]
    print(len(df))

    df = df[df['Хакасский'].str.count('\\w+') >= 5]
    print(len(df))

    df = df.drop(df[df['Хакасский'] == df['Русский']].index)
    print(len(df))

    pattern = '|'.join(['ғ', 'ң', 'ӧ', 'ӱ'])
    df = df[~df['Русский'].str.contains(pattern)]
    print(len(df))

    df.to_csv(save_path, index=False)


def drop_mono():
    path = '../data/mono_fix_symbols.csv'
    save_path = '../data/mono_fix_symbols_drop.csv'
    assert not os.path.exists(save_path)

    df = pd.read_csv(path)
    print(len(df))

    df = df.dropna(subset=['Хакасский'])
    print(len(df))

    df = df[df['Хакасский'].str.count('\\w+') >= 5]
    print(len(df))

    df = df[df['Хакасский'].str.count('\\w+') <= 20]
    print(len(df))

    kjh_symbols = list('ІіҒғҢңҶҷӦӧӰӱ')
    pattern = '|'.join(kjh_symbols)
    df = df[df['Хакасский'].str.contains(pattern)]
    print(len(df))
    print(df['word_len'].describe())
    print(df['Источник'].value_counts())

    df.to_csv(save_path, index=False)


if __name__ == "__main__":
    drop_mono()
