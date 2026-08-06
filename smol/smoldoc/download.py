from datasets import load_dataset


def main():
    ds = load_dataset("adeshkin/google-smol-en-ru-kjh", 'smoldoc', split='train')
    df = ds.to_pandas()
    print(df.head())
    print(len(df))
    df.to_csv('smoldoc_kjh.csv')


if __name__ == '__main__':
    main()
