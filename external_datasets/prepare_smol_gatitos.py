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

    results = {}
    en_sents = set()
    for name in names:
        results[name] = dict()
        ds = load_dataset("google/smol", name)
        examples = []
        for example in ds['train']:
            examples.append(example)

        for ex in examples:
            assert ex['sl'] == 'en'
            assert ex['is_source_orig']
            en_sents.add(ex['src'])
            if ex['src'] in results[name]:
                results[name][ex['src']] = results[name][ex['src']] + ['###'] + ex['trgs']
            else:
                results[name][ex['src']] = ex['trgs']

    examples = []
    for sent in en_sents:
        example = [sent]
        for name in names:
            if sent in results[name]:
                example.append(results[name][sent])
            else:
                example.append(None)
        examples.append(example)

    df = pd.DataFrame(examples, columns=['en'] + names)
    df.to_csv('smol_gatitos.csv', index=False)


if __name__ == '__main__':
    main()