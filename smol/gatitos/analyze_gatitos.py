import json
import pandas as pd


def main():
    with open('gatitos_yandex_dict_result_error.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    no_trans = []
    for word in data:
        if len(data[word]['def']) == 0:
            print(word)
            print(data[word])
            no_trans.append(word)

    df = pd.DataFrame(no_trans, columns=['en'])
    df.to_excel('gatitos_294_yandex_translate.xlsx', index=False, header=False)


def main1():
    with open('gatitos_yandex_dict_result_error.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    word2trans = {}
    for word in data:
        if len(data[word]['def']) != 0:
            word2trans[word] = {}
            for i in range(len(data[word]['def'])):
                for j in range(len(data[word]['def'][i]['tr'])):
                    value = data[word]['def'][i]['tr'][j]
                    word2trans[word][f'{i:04d}_{j:04d}'] = {k: v for k, v in value.items()
                                                            if k in ['text', 'gen', 'pos', 'fr', 'num']}

    print(len(word2trans))




if __name__ == '__main__':
    main1()

