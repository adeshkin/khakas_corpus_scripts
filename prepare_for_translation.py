import pandas as pd
from razdel import sentenize, tokenize
from sklearn.model_selection import train_test_split

pd.set_option('display.max_colwidth', None)


def get_word_count(text):
    tokens = list(tokenize(text))
    words = [token.text for token in tokens if any(c.isalpha() for c in token.text)]

    return len(words)


def prepare_for_translation():
    df = pd.read_parquet("hf://datasets/adeshkin/khakas-monolingual-corpus/data/train-00000-of-00001.parquet")
    print(len(df))
    kjh_sents = df[df['source'] == 'Articles from "Khakas Chiry" newspaper']['kjh'].values.tolist()
    print(len(kjh_sents))
    all_kjh_sents = []
    for kjh_sent in kjh_sents:
        sentences = [s.text for s in sentenize(kjh_sent)]
        all_kjh_sents.extend(sentences)

    df = pd.DataFrame(all_kjh_sents, columns=['kjh'])
    df['kjh_wlen'] = df['kjh'].apply(lambda x: get_word_count(x))
    df = df[(df['kjh_wlen'] >= 6) & (df['kjh_wlen'] <= 20)]
    print(len(df))
    print(df['kjh_wlen'].value_counts(normalize=True))

    sampled_df, _ = train_test_split(
        df,
        train_size=50000,
        stratify=df['kjh_wlen'],
        random_state=42  # Для воспроизводимости результата
    )

    print(sampled_df.shape)
    print(sampled_df['kjh_wlen'].value_counts(normalize=True))
    sampled_df = sampled_df.drop(columns=['kjh_wlen'])
    print(sampled_df.columns)

    sampled_df.to_excel('khakas_50k_to_translate.xlsx', index=False)


if __name__ == '__main__':
    prepare_for_translation()
