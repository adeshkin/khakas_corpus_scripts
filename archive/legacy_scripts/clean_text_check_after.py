import os
import json
import pylcs
import numpy as np
import time
import pandas as pd
import random
import re


def main():
    df1 = pd.read_csv("/home/adeshkin/Downloads/uchebniki_table_for_lcs.csv")
    df = df1[(df1['len']>=10)&(df1['len']<=50)]
    examples = df['only_words'].values.tolist()
    khakas_sentences = df['khakas_sentence'].values.tolist()

    with open("all_indexes.txt", "r") as f:
        all_indexes = set(map(int, f.read().splitlines()))

    sents_8_28 = []
    for i in range(len(khakas_sentences)):
        if i in all_indexes:
            continue

        sents_8_28.append(khakas_sentences[i])

    random.shuffle(sents_8_28)
    num_sents = 50
    num_sents_per_folder = 500
    save_dir = '/home/adeshkin/Desktop/uchebniki_docx'
    os.makedirs(save_dir)
    for i in range(0, len(sents_8_28), num_sents):
        if i == 0 or i % num_sents_per_folder == 0:
            new_dir = f'{save_dir}/translated_{i:04}'
            os.makedirs(new_dir)
        with open(f'{new_dir}/{i:04}.txt', 'w') as f:
            f.write('# СТРОКИ ДЛЯ ПЕРЕВОДА НАЧАЛО\n')
            for sent in sents_8_28[i:i + num_sents]:
                f.write(f'{sent}\n')
            f.write('# СТРОКИ ДЛЯ ПЕРЕВОДА КОНЕЦ')









if __name__ == "__main__":
    main()