import difflib
import random

import pandas as pd
from glob import glob
import json


def find_ru_files():
    data_dir = '/home/adeshkin/khakas_projects/smol/smoldoc'
    paths = sorted(glob(f'{data_dir}/ru*.jsonl'))
    paths += sorted(glob(f'{data_dir}/*ru.jsonl'))
    # ru_abq ru_ce ru_jdt
    paths = sorted(glob(f'{data_dir}/abq*.jsonl'))
    paths += sorted(glob(f'{data_dir}/*abq.jsonl'))
    print(*paths, sep='\n')


def prepare_smolsent_ru_kjh():
    df1 = pd.read_parquet("hf://datasets/adeshkin/google-smol-en-ru-kjh/smolsent/train-00000-of-00001.parquet")
    df2 = pd.read_json('/home/adeshkin/khakas_projects/smol/smolsent/ru_ce.jsonl', lines=True)
    assert len(df1) == len(df2)

    df2['sl'] = 'ru'
    df2['tl'] = 'kjh'
    df2['src'] = df1['ru']
    df2['trg'] = df1['kjh']
    df2['is_src_orig'] = True

    output_path = "/home/adeshkin/khakas_projects/smol/smolsent/ru_kjh.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for record in df2.to_dict(orient="records"):
            line = json.dumps(
                record,
                separators=(", ", ": "),
            )
            f.write(line + "\n")

    df2['sl'] = 'kjh'
    df2['tl'] = 'ru'
    df2['src'] = df1['kjh']
    df2['trg'] = df1['ru']
    df2['is_src_orig'] = False

    output_path = "/home/adeshkin/khakas_projects/smol/smolsent/kjh_ru.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for record in df2.to_dict(orient="records"):
            line = json.dumps(
                record,
                separators=(", ", ": "),
            )
            f.write(line + "\n")


def prepare_smolsent_en_kjh():
    df1 = pd.read_parquet("hf://datasets/adeshkin/google-smol-en-ru-kjh/smolsent/train-00000-of-00001.parquet")
    df2 = pd.read_json('/home/adeshkin/khakas_projects/smol/smolsent/en_tyv.jsonl', lines=True)
    assert len(df1) == len(df2)

    df2['sl'] = 'en'
    df2['tl'] = 'kjh'
    df2['src'] = df1['en']
    df2['trg'] = df1['kjh']
    df2['is_src_orig'] = True

    output_path = "/home/adeshkin/khakas_projects/smol/smolsent/en_kjh.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for record in df2.to_dict(orient="records"):
            line = json.dumps(
                record,
                separators=(", ", ": "),
            )
            f.write(line + "\n")

    df2['sl'] = 'kjh'
    df2['tl'] = 'en'
    df2['src'] = df1['kjh']
    df2['trg'] = df1['en']
    df2['is_src_orig'] = False

    output_path = "/home/adeshkin/khakas_projects/smol/smolsent/kjh_en.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for record in df2.to_dict(orient="records"):
            line = json.dumps(
                record,
                separators=(", ", ": "),
            )
            f.write(line + "\n")


def prepare_smoldoc_ru_kjh():
    df = pd.read_parquet("hf://datasets/adeshkin/google-smol-en-ru-kjh/smoldoc/train-00000-of-00001.parquet")
    data = df[['en', 'ru', 'kjh']].values.tolist()
    id2en_data = {}
    id2ru_data = {}
    id2kjh_data = {}
    for row in data:
        if row[0].startswith('ID='):
            assert row[1] == ''
            assert row[2] == ''
            idx = row[0].split('ID=')[1]
            id2en_data[idx] = []
            id2ru_data[idx] = []
            id2kjh_data[idx] = []

        if row[1] != '':
            id2en_data[idx].append(row[0])
            id2ru_data[idx].append(row[1])
            id2kjh_data[idx].append(row[2])


    # print(len(id2data))
    # print(id2data['topic_394__dittfcismttb'])

    df2 = pd.read_json('/home/adeshkin/khakas_projects/smol/smoldoc/ru_ce.jsonl', lines=True)
    df2['sl'] = 'ru'
    df2['tl'] = 'kjh'
    # df2 = df2.drop(columns=['srcs', 'trgs'])
    df2['srcs'] = df2['id'].map(id2ru_data)
    df2['trgs'] = df2['id'].map(id2kjh_data)
    df2['is_src_orig'] = True

    assert df2['srcs'].isna().sum() == 0
    assert df2['trgs'].isna().sum() == 0

    output_path = "/home/adeshkin/khakas_projects/smol/smoldoc/ru_kjh.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for record in df2.to_dict(orient="records"):
            line = json.dumps(
                record,
                separators=(", ", ": "),
            )
            f.write(line + "\n")

    df2['sl'] = 'kjh'
    df2['tl'] = 'ru'
    print(len(df2))
    # df2 = df2.drop(columns=['srcs', 'trgs'])
    df2['srcs'] = df2['id'].map(id2kjh_data)
    df2['trgs'] = df2['id'].map(id2ru_data)
    df2['is_src_orig'] = False

    assert df2['srcs'].isna().sum() == 0
    assert df2['trgs'].isna().sum() == 0

    output_path = "/home/adeshkin/khakas_projects/smol/smoldoc/kjh_ru.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for record in df2.to_dict(orient="records"):
            line = json.dumps(
                record,
                separators=(", ", ": "),
            )
            f.write(line + "\n")


def check_smolsent():
    df = pd.read_json('/home/adeshkin/khakas_projects/smol/smolsent/ru_kjh.jsonl', lines=True)
    df1 = pd.read_json('/home/adeshkin/khakas_projects/smol/smolsent/kjh_ru.jsonl', lines=True)
    df_ce = pd.read_json('/home/adeshkin/khakas_projects/smol/smolsent/ru_ce.jsonl', lines=True)
    df_en = pd.read_json('/home/adeshkin/khakas_projects/smol/smolsent/en_es.jsonl', lines=True)
    # print(df.columns)
    assert (df['sl'] == 'ru').all()
    assert (df['tl'] == 'kjh').all()
    assert (df['id'] == df_en['id']).all()
    assert (df['is_src_orig'] == True).all()
    assert (df['id'] == df_ce['id']).all()

    assert (df1['sl'] == 'kjh').all()
    assert (df1['tl'] == 'ru').all()
    assert (df1['id'] == df_en['id']).all()
    assert (df1['is_src_orig'] == False).all()
    assert (df1['id'] == df_ce['id']).all()
    assert (df1['src'] == df['trg']).all()
    assert (df1['trg'] == df['src']).all()
    # assert (df['src'] == df_ce['src']).all()
    df['ce_src'] = df_ce['src']
    pairs = df[df['src'] != df['ce_src']][['src', 'ce_src']].values.tolist()
    print(len(pairs))
    for pair in pairs:
        ex1 = pair[0].replace("-", "—")
        ex2 = pair[1].replace("-", "—")
        if ex1 != ex2:
            print(pair[0])
            print(pair[1])
            result = difflib.ndiff(pair[0], pair[1])
            print(''.join(result))
            print()

    df_src = pd.read_parquet("hf://datasets/adeshkin/google-smol-en-ru-kjh/smolsent/train-00000-of-00001.parquet")
    mapping = df_src.drop_duplicates(subset=['ru']).set_index('ru')['en']
    df['en'] = df['src'].map(mapping)
    assert df['en'].isna().sum() == 0
    df['en_orig'] = df_en['src']
    pairs = df[df['en'] != df['en_orig']][['en', 'en_orig']].values.tolist()
    # print(len(pairs))
    # for pair in pairs:
    #     ex1 = pair[0].replace("'", "’")
    #     ex2 = pair[1].replace("'", "’")
    #     if ex1 != ex2:
    #         print(pair[0])
    #         print(pair[1])
    #         print()

def check_smoldoc():
    df = pd.read_json('/home/adeshkin/khakas_projects/smol/smoldoc/ru_kjh.jsonl', lines=True)
    df1 = pd.read_json('/home/adeshkin/khakas_projects/smol/smoldoc/kjh_ru.jsonl', lines=True)

    assert (df['sl'] == 'ru').all()
    assert (df['tl'] == 'kjh').all()
    assert (df['is_src_orig'] == True).all()

    assert (df1['sl'] == 'kjh').all()
    assert (df1['tl'] == 'ru').all()
    assert (df1['is_src_orig'] == False).all()

    assert (df1['srcs'] == df['trgs']).all()
    assert (df1['trgs'] == df['srcs']).all()
    assert (df1['id'] == df['id']).all()

    df_ce = pd.read_json('/home/adeshkin/khakas_projects/smol/smoldoc/en_tyv.jsonl', lines=True)
    assert (df['id'] == df_ce['id']).all()
    #assert (df['srcs'] == df_ce['srcs']).all()
    df_src_smol = pd.read_parquet("hf://datasets/adeshkin/google-smol-en-ru-kjh/smoldoc/train-00000-of-00001.parquet")
    data = df_src_smol[['en', 'ru', 'kjh']].values.tolist()
    id2en_data = {}
    id2ru_data = {}
    id2kjh_data = {}
    for row in data:
        if row[0].startswith('ID='):
            assert row[1] == ''
            assert row[2] == ''
            idx = row[0].split('ID=')[1]
            id2en_data[idx] = []
            id2ru_data[idx] = []
            id2kjh_data[idx] = []

        if row[1] != '':
            id2en_data[idx].append(row[0])
            id2ru_data[idx].append(row[1])
            id2kjh_data[idx].append(row[2])

    df['en'] = df['id'].map(id2en_data)
    df['en_tyv'] = df_ce['srcs']
    pairs = df[df['en'] != df['en_tyv']][['en', 'en_tyv']].values.tolist()
    print(len(pairs))
    import re
    def clean_text(text):
        text = ' '.join(re.findall(r'[^\W\d_]+', text))
        text = re.sub(r'\\s+', ' ', text)

        return text.strip()
    for pair in pairs:
        for ex1, ex2 in zip(pair[0], pair[1]):
            ex2 = clean_text(ex2)
            ex1 =  clean_text(ex1)
            # print(ex1)
            # print(ex2)
            # print()
            if ex1 != ex2:
                print(ex1)
                print(ex2)
                result = difflib.ndiff(ex1, ex2)
                print(''.join(result))
                print()


if __name__ == '__main__':
    # prepare_smolsent_ru_kjh()
    # prepare_smoldoc_ru_kjh()
    pd.set_option('display.max_colwidth', None)
    df = pd.read_json('/home/adeshkin/khakas_projects/smol/smoldoc/ru_kjh.jsonl', lines=True)
    pairs = df[['srcs', 'trgs']].values.tolist()
    pair = random.choice(pairs)
    for sent1, sent2 in zip(pair[0], pair[1]):
        print(sent1)
        print(sent2)
        print()