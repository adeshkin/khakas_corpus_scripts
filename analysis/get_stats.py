import unicodedata

import pandas as pd


def main():
    # path = '/home/adeshkin/khakas_projects/data/translation/parallel_corpus/khakas_russian_parallel_corpus_v1.csv'
    # df = pd.read_csv(path)
    # kjh_sents = df['Хакасский'].values.tolist()
    # text = ' '.join(kjh_sents)
    with open('/home/adeshkin/khakas_projects/khakas-mt/data/final/mono_para_kjh.txt', 'r') as f:
        text = f.read()

    text = text.lower()

    print(repr(''.join(sorted(set(text)))))
    symbol_stats = []
    for ch in 'абвгдежзийклмнопрстуфхцчшщъыьэюяёіғңҷӧӱ':
        symbol_stats.append((ch, text.count(ch)))

    symbol_stats = sorted(symbol_stats, key=lambda x: x[1], reverse=True)
    print(repr(symbol_stats))





if __name__ == '__main__':
    main()
    print('іғңҷӧӱ'.upper())
