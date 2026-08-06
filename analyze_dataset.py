from datasets import load_dataset

dataset = load_dataset('adeshkin/khakas-russian-parallel-corpus', split='train')
df = dataset.to_pandas()
from razdel import tokenize


def get_word_count(text):
    tokens = list(tokenize(text))
    words = [token.text for token in tokens if any(c.isalpha() for c in token.text)]

    return len(words)


df['kjh_wlen'] = df['kjh'].apply(lambda x: get_word_count(x))
df['ru_wlen'] = df['ru'].apply(lambda x: get_word_count(x))
print(df['kjh_wlen'].describe())
print(sum(df['kjh_wlen'].tolist()))
print(df['ru_wlen'].describe())
print(sum(df['ru_wlen'].tolist()))