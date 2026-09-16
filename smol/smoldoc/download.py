from datasets import load_dataset


def main():
    ds = load_dataset("adeshkin/khakas-russian-dict", 'default', split='train')
    ds = ds.select_columns(['word', 'semgloss', 'field1'])
    df = ds.to_pandas()
    print(df.columns)
    print(len(df))
    df.to_csv('/home/adeshkin/khakas_projects/gatitos_review/khakas-russian-dict.csv', index=False)


def main1():
    ds = load_dataset("adeshkin/khakas-explanatory-dict", split='train')
    ds = ds.select_columns(['headword_fix', 'field_fix'])
    df = ds.to_pandas()
    print(df.columns)
    print(len(df))
    df.to_csv('/home/adeshkin/khakas_projects/gatitos_review/khakas-explanatory-dict.csv', index=False)


def main2():
    ds = load_dataset("adeshkin/russian-khakas-literary-dict", split='train')
    ds = ds.select_columns(['headword_fix', 'field_fix'])
    df = ds.to_pandas()
    print(df.columns)
    print(len(df))
    df.to_csv('/home/adeshkin/khakas_projects/gatitos_review/russian-khakas-literary-dict.csv', index=False)


def main3():
    ds = load_dataset("adeshkin/russian-khakas-base-phrases", split='train')
    ds = ds.select_columns(['ru', 'kjh'])
    df = ds.to_pandas()
    print(df.columns)
    print(len(df))
    df.to_csv('/home/adeshkin/khakas_projects/gatitos_review/russian-khakas-base-phrases.csv', index=False)


if __name__ == '__main__':
    main()
    main1()
    main2()
    main3()
