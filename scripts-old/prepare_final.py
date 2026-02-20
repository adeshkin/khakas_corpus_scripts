import numpy as np
import pandas as pd

pd.set_option('display.max_colwidth', None)


def main():
    path = 'data/Кулумаева - 1.csv'
    df = pd.read_csv(path)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    print(len(df))
    df.dropna(subset=['Хакасский'], inplace=True)
    df.dropna(subset=['Русский'], inplace=True)
    print(len(df))
    print()

    df['not_valid'] = df.apply(lambda x: len(x['Хакасский']) < 20, axis=1)
    print(df[df['not_valid']][['Русский', 'Хакасский']])
    print()

    df['not_valid'] = df.apply(lambda x: len(x['Русский']) < 20, axis=1)
    print(df[df['not_valid']][['Русский', 'Хакасский']])
    print()

    print(df['Отредактированный_Хакасский'].describe())

    df['Russian'] = df['Русский']
    df['Khakas'] = df.apply(
        lambda x: x['Хакасский'] if pd.isna(x['Отредактированный_Хакасский']) else x['Отредактированный_Хакасский'], axis=1)

    df.drop(columns=['Русский', 'Хакасский', 'Отредактированный_Хакасский', 'not_valid'], inplace=True)
    df = df.reindex(columns=['Russian', 'Khakas', 'Переводчик', 'Редактор'])
    print(len(df))

    df.to_csv(path.replace('Кулумаева', 'Кулумаева_готовый'), index=False)






if __name__ == '__main__':
    main()
