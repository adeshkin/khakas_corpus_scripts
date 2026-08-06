import pandas as pd


def main():
    data_dir = '/home/adeshkin/khakas_projects/khakas-language-resources/khakas_texts_with_russian_translation/data'
    splits = ['train', 'val', 'test']

    pairs = []
    for split in splits:
        df = pd.read_csv(data_dir + '/' + split + '.csv')
        pairs.extend(df[['kjh', 'ru']].values.tolist())

    df = pd.DataFrame(pairs, columns=['Хакасский', 'Русский'])
    df['Источник'] = 'khakas-language-resources'
    print(len(df))
    df.to_csv('/home/adeshkin/khakas_projects/data/translation/khakas-language-resources/klr.csv', index=False)


if __name__ == '__main__':
    main()
