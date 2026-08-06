from sacremoses import MosesDetokenizer
import pandas as pd

pd.set_option('display.max_colwidth', None)

md = MosesDetokenizer(lang='ru')


def main():
    path = '../data/final/para_kjh_ru.csv'  # mono_kjh para_kjh_ru
    df = pd.read_csv(path)

    names = df['source'].unique().tolist()
    for name in names:
        if name == 'khakas-language-resources' or name == 'til':
            print(name)
            samples = df[df['source'] == name]['kjh'].sample(5)
            print(samples)
            bad_text = samples.values.tolist()[0]
            tokens = bad_text.split()
            good_text = md.detokenize(tokens)
            print()
            print(bad_text)
            print(good_text)
            print()

            print('\n\n\n')


if __name__ == '__main__':
    main()
