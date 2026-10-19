import unicodedata

from datasets import Dataset, load_dataset
import pandas as pd

import re
import unicodedata


def find_words_with_symbol(text, symbol):
    words = re.findall(r'\b\w*' + re.escape(symbol) + r'\w*\b', text)
    # words = re.findall(r'.{0,15}' + re.escape(symbol) + r'.{0,15}', text)

    return sorted(set(words))

def check():
    df = pd.read_csv("/home/adeshkin/Downloads/diversity500_khakas.xlsx - Лист1.csv")
    df.rename(columns={'хакасский': 'kjh', 'русский': 'ru'}, inplace=True)
    df['ru'] = df['ru'].apply(lambda x: x.strip())
    df['kjh'] = df['kjh'].apply(lambda x: x.strip())
    print(df.columns)

    assert df['kjh'].isna().sum() == 0
    assert df['ru'].isna().sum() == 0
    assert len(df[df['kjh'].str.len() < 1]) == 0
    assert len(df[df['ru'].str.len() < 2]) == 0

    kjh_sents = df['kjh'].values.tolist()
    text = ' '.join(kjh_sents)
    assert 'іғңҷӦӧӰӱ' == 'іғңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ
    print(repr(''.join(sorted(set(text)))))

    for symbol in '@ACEFGHILMNPRSTUVWX[]acdefghiklmnorstuwy':
        words = find_words_with_symbol(text, symbol)
        if len(words) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(words))
            print(*words, sep='\n')
            print()

    kjh_sents = df['ru'].values.tolist()
    text = ' '.join(kjh_sents)
    print(repr(''.join(sorted(set(text)))))

    for symbol in '':
        words = find_words_with_symbol(text, symbol)
        if len(words) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(words))
            print(*words, sep='\n')
            print()
    #
    # # islower()
    # ru_lower_but_kjh_not = df[df['ru'].str.istitle() & ~df['kjh'].str.istitle()]
    # assert len(
    #     ru_lower_but_kjh_not) == 0, f"Найдено строк, где 'ru' в нижнем регистре, а 'kjh' — нет:\n{ru_lower_but_kjh_not.head(10)}"
    #
    # kjh_lower_but_ru_not = df[df['kjh'].str.istitle() & ~df['ru'].str.istitle()]
    # assert len(
    #     kjh_lower_but_ru_not) == 0, f"Найдено строк, где 'kjh' в нижнем регистре, а 'ru' — нет:\n{kjh_lower_but_ru_not.head()}"
    #
    # print(df)
def push_new_dataset():
    df = pd.read_csv("/home/adeshkin/Downloads/flores_plus_kjh_rus_dev.csv")
    print(df.columns)
    # df.rename(columns={'хакасский': 'kjh', 'русский': 'ru', 'источник': 'source'}, inplace=True)
    hf_dataset = Dataset.from_pandas(df, preserve_index=False)

    REPOSITORY_ID = "adeshkin/openlanguagedata-flores-plus"
    HF_TOKEN = ""

    hf_dataset.push_to_hub(
        repo_id=REPOSITORY_ID,
        token=HF_TOKEN,
        split='dev'
    )
    #
    # print(f"Датасет успешно загружен в https://huggingface.co{REPOSITORY_ID}")


def align_flores_translations(khakas, russian):
    """Return Khakas and Russian FLORES+ texts aligned by sentence ID."""
    if khakas["id"].duplicated().any() or russian["id"].duplicated().any():
        raise ValueError("FLORES+ sentence IDs must be unique within a split")

    khakas_ids = set(khakas["id"])
    russian_ids = set(russian["id"])
    if khakas_ids != russian_ids:
        raise ValueError("Khakas and Russian FLORES+ sentence IDs do not match")

    return khakas[["id", "text"]].rename(columns={"text": "kjh"}).merge(
        russian[["id", "text"]].rename(columns={"text": "ru"}),
        on="id",
        how="left",
        validate="one_to_one",
        sort=False,
    )


def download_dataset():
    khakas = load_dataset(
        "openlanguagedata/flores_plus", "kjh_Cyrl", split="devtest"
    ).to_pandas()
    russian = load_dataset(
        "openlanguagedata/flores_plus", "rus_Cyrl", split="devtest"
    ).to_pandas()
    aligned = align_flores_translations(khakas, russian)
    aligned.to_csv(
        "/home/adeshkin/Downloads/flores_plus_kjh_rus_devtest.csv",
        index=False,
    )

if __name__ == '__main__':
    # download_dataset()
    push_new_dataset()
