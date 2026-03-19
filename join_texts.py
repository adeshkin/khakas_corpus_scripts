import pandas as pd


def main():
    path = '/home/adeshkin/Downloads/khakaschiry.csv'
    df = pd.read_csv(path)
    print(len(df))

    df = df.dropna(subset=['text'])
    print(len(df))

    df = df[df['text'].str.count('\\w+') >= 10]
    print(len(df))

    texts = df['text'].tolist()
    print(len(texts))

    full_text = '\n\n\n#####\n\n\n'.join(texts)

    with open('/home/adeshkin/khakas_projects/data/mono/khakaschiry.txt', 'w', encoding='utf-8') as f:
        f.write(full_text)


def main1():
    path = '/home/adeshkin/Downloads/vk_ah_tashyl - vk_ah_tashyl.csv'
    df = pd.read_csv(path)
    print(len(df))

    df = df.dropna(subset=['text'])
    print(len(df))

    df = df[df['text'].str.count('\\w+') >= 3]
    print(len(df))

    texts = df['text'].tolist()
    print(len(texts))

    full_text = '\n\n\n#####\n\n\n'.join(texts)

    with open('/home/adeshkin/khakas_projects/data/mono/vk_ah_tashyl.txt', 'w', encoding='utf-8') as f:
        f.write(full_text)


if __name__ == '__main__':
    main()
    main1()
