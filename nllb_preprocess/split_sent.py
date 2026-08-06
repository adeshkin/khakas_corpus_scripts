import re
import os
from glob import glob
import pandas as pd
from razdel import sentenize


def get_word_count(text):
    word_count = len(re.findall(r'[^\W\d_]+', text))

    return word_count


def split_sent(text, max_words_per_chunk=12):
    sentences = [s.text for s in sentenize(text)]

    chunks = []
    buffer = []
    buffer_word_count = 0

    for sentence in sentences:
        word_count = get_word_count(sentence)

        if word_count >= max_words_per_chunk:
            if buffer:
                chunks.append(" ".join(buffer))
                buffer = []
                buffer_word_count = 0

            chunks.append(sentence)
        else:
            if buffer_word_count + word_count > max_words_per_chunk:
                chunks.append(" ".join(buffer))
                buffer = [sentence]
                buffer_word_count = word_count
            else:
                buffer.append(sentence)
                buffer_word_count += word_count

    if buffer:
        chunks.append(" ".join(buffer))

    return chunks


def split_para(text):
    paras = text.split('\n')

    return paras


def main():
    data_dir = '/home/adeshkin/khakas_projects/data/mono'
    save_path = '../data/mono_kc_rn_at.csv'
    assert not os.path.exists(save_path)

    paths = sorted(glob(os.path.join(data_dir, '*.txt')))
    result = {}
    for path in paths:
        name = os.path.basename(path).split('.')[0]
        with open(path, 'r') as f:
            text = f.read()

        paras = split_para(text)
        sents = []
        for para in paras:
            sents.extend(split_sent(para))

        result[name] = sents

    rows = []
    for name, sents in result.items():
        print(name, len(sents))
        for sent in sents:
            rows.append({'Хакасский': sent, 'Источник': name})

    df = pd.DataFrame(rows, columns=['Хакасский', 'Источник'])
    print(len(df))

    df = df.dropna(subset=['Хакасский'])
    print(len(df))

    df['word_len'] = df['Хакасский'].apply(get_word_count)

    df = df[df['word_len'] >= 5]
    print(len(df))

    df = df[df['word_len'] <= 20]
    print(len(df))

    print(df['word_len'].describe())
    print(df['Источник'].value_counts())


    df.to_csv(save_path, index=False)


def main_alpaca():
    data_dir = '/home/adeshkin/Downloads/ru_alpaca_seed_tasks'
    save_path = '/home/adeshkin/Downloads/ru_alpaca_seed_tasks/output_instances.csv'
    assert not os.path.exists(save_path)

    paths = sorted(glob(os.path.join(data_dir, 'output*.txt')))
    result = {}
    for path in paths:
        name = os.path.basename(path).split('.')[0]
        with open(path, 'r') as f:
            text = f.read()

        paras = split_para(text)
        sents = []
        for para in paras:
            sents.extend(split_sent(para))

        result[name] = sents

    rows = []
    for name, sents in result.items():
        print(name, len(sents))
        for sent in sents:
            rows.append({'Русский': sent.strip(), 'Источник': name})

    df = pd.DataFrame(rows, columns=['Русский', 'Источник'])
    print(len(df))

    df = df.dropna(subset=['Русский'])
    print(len(df))

    df['word_len'] = df['Русский'].apply(get_word_count)
    df = df[df['word_len'] >= 1]

    print(df['word_len'].describe())
    print(df['Источник'].value_counts())


    df.to_csv(save_path, index=False)

if __name__ == '__main__':
    main_alpaca()
