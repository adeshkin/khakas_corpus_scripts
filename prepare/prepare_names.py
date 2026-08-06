import pandas as pd


def main():
    path = '/home/adeshkin/Downloads/список людей - Sheet1.csv'
    df = pd.read_csv(path, header=None)
    print(df.head())
    print(len(df))
    print(', '.join(df[0].tolist()))


if __name__ == '__main__':
    main()
