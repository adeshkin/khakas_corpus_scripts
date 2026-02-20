import os
import json
import pylcs
import numpy as np
import time
import pandas as pd
import random


def main():
    df1 = pd.read_csv("/home/adeshkin/Downloads/uchebniki_table_for_lcs.csv")
    df = df1[(df1['len']>=10)&(df1['len']<=50)]
    examples = df['only_words'].values.tolist()
    khakas_sentences = df['khakas_sentence'].values.tolist()

    with open("all_indexes.txt", "r") as f:
        all_indexes = set(map(int, f.read().splitlines()))

    with open("all_indexes.json", "r") as f:
        id2indexes = json.load(f)

    i = random.choice(list(id2indexes.keys()))
    example = examples[int(i)]
    threshold = 0.5 * len(example)
    start_time = time.perf_counter()
    longest_common_substring_lengths = np.array(pylcs.lcs_string_of_list(example, examples))
    ids = np.where(longest_common_substring_lengths >= threshold)[0]
    print(i)
    print(ids)
    print(id2indexes[i])
    print(khakas_sentences[int(i)])
    print("#"*100)
    for idx in ids:
        if idx != int(i):
            print(khakas_sentences[idx])





if __name__ == "__main__":
    main()