from datasets import load_dataset
import pandas as pd


def main():
    names = ['gatitos__en_ace',
             'gatitos__en_ady',
             'gatitos__en_av',
             'gatitos__en_udm',
             'gatitos__en_ba',
             'gatitos__en_bua',
             'gatitos__en_chm',
             'gatitos__en_cv',
             'gatitos__en_kv',
             'gatitos__en_sah',
             'gatitos__en_tyv']

    # results = {}
    en_sents = dict()
    for name in names:
        # results[name] = dict()
        ds = load_dataset("google/smol", name)
        # examples = []
        for example in ds['train']:
            # examples.append(example)
            assert example['sl'] == 'en'
            assert example['is_source_orig']
            en_sents.setdefault(example['src'], None)

        # Код сбора переводов больше не нужен: сохраняем только английские
        # исходные предложения из поля src.
        # for ex in examples:
        #     if ex['src'] in results[name]:
        #         results[name][ex['src']] = results[name][ex['src']] + ['###'] + ex['trgs']
        #     else:
        #         results[name][ex['src']] = ex['trgs']

    df = pd.DataFrame(list(en_sents), columns=['en'])
    df.to_csv('smol_gatitos.csv', index=False)


if __name__ == '__main__':
    main()
