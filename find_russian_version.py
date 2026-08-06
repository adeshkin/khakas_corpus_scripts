def main():
    import pandas as pd

    df = pd.read_parquet("hf://datasets/adeshkin/khakas-russian-parallel-corpus/data/train-00000-of-00001.parquet")
    print(len(df))
    price_map = df.set_index('kjh')['ru']
    df1 = pd.read_csv('/home/adeshkin/Downloads/Чебочакова Ирина Максимовна - 2026 - Copy of common_voice_sent.csv')
    df1['ru'] = df1['Хакасский (Исходный)'].map(price_map)
    print(len(df1))
    df1 = df1.dropna(subset=['ru'])
    print(len(df1))
    df1.to_csv('/home/adeshkin/Downloads/Чебочакова Ирина Максимовна - 2026 - Copy of common_voice_sent_fixed.csv')


if __name__ == '__main__':
    main()