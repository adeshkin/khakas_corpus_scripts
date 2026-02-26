import pandas as pd

def main():
    df = pd.read_csv('/home/adeshkin/Downloads/hrs_new34_word_field1_fixed.csv')
    print(df.head())
    print(df.info())


if __name__ == '__main__':
    main()