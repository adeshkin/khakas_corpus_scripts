import os
import json
import pylcs
import numpy as np
import time
import pandas as pd


def main():
    df1 = pd.read_csv("/home/adeshkin/Downloads/uchebniki_table_for_lcs.csv")
    df = df1[(df1['len']>=10)&(df1['len']<=50)]
    examples = df['only_words'].values.tolist()
    khakas_sentences = df['khakas_sentence'].values.tolist()

    with open("all_indexes_7100.txt", "r") as f:
        all_indexes = set(map(int, f.read().splitlines()))

    with open("all_indexes_7100.json", "r") as f:
        id2indexes = json.load(f)
    #all_indexes = set()
    #id2indexes = dict()
    for i in range(7050, len(examples)):
        if i in all_indexes:
            continue
        example = examples[i]
        threshold = 0.5 * len(example)
        start_time = time.perf_counter()
        longest_common_substring_lengths = np.array(pylcs.lcs_string_of_list(example, examples))
        ids = np.where(longest_common_substring_lengths >= threshold)[0]
        end_time = time.perf_counter()

        if len(ids) > 1:
            print(end_time - start_time)
            print(i)
            print(khakas_sentences[i])
            print()
            print(ids)
            for idx in ids:
                if idx != i:
                    print(khakas_sentences[idx])
            print("#"*100)
            print()

        if len(ids) > 1:
            all_indexes = set(all_indexes).union(set(ids))
            id2indexes[int(i)] = [int(x) for x in list(set(ids))]

        if (i+1) % 100 == 0 or i == (len(examples) - 1):
            print(f"\n\nProcessed {i+1}/{len(examples)}")
            print(end_time - start_time)
            print("\n")
            old_name = f"all_indexes_{i+1-100}.txt"
            new_name = f"all_indexes_{i+1}.txt"
            if os.path.exists(old_name):
                os.remove(old_name)
                os.remove(old_name.replace(".txt", ".json"))
            with open(new_name.replace(".txt", ".json"), "w") as f:
                json.dump(id2indexes, f)

            with open(new_name, "w") as f:
                f.write("\n".join(map(str, list(all_indexes))))

    with open("all_indexes.txt", "w") as f:
        f.write("\n".join(map(str, list(all_indexes))))
    with open("all_indexes.json", "w") as f:
        json.dump(id2indexes, f)



if __name__ == "__main__":
    main()