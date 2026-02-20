from datasets import load_dataset

names = ['gatitos__en_ace', 'gatitos__en_ba', 'gatitos__en_bua', 'gatitos__en_chm', 'gatitos__en_cv', 'gatitos__en_kv', 'gatitos__en_sah', 'gatitos__en_tyv']
sents = list()

for name in names:
    ds = load_dataset("google/smol", name)
    examples = []
    for example in ds['train']:
        examples.append(example)

    for ex in examples:
        assert ex['sl'] == 'en'
        assert ex['is_source_orig']
        sents.append(ex['src'])