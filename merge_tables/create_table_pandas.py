import pandas as pd


def main():
    with open('/home/adeshkin/khakas_projects/data/translation/little_prince/prince_kjh_ru_khakas.txt') as f:
        kjh_lines = f.readlines()
    with open('/home/adeshkin/khakas_projects/data/translation/little_prince/prince_kjh_ru_russian.txt') as f:
        ru_lines = f.readlines()

    assert len(kjh_lines) == len(ru_lines)

    df = pd.DataFrame({'Russian': ru_lines, 'Khakas': kjh_lines})
    print(df.head())

    df.to_csv('/home/adeshkin/khakas_projects/data/translation/little_prince/prince_kjh_ru_russian_khakas.csv',
              index=False)


def save_to_file():
    df = pd.read_csv(
        '/home/adeshkin/khakas_projects/data/translation/little_prince/prince_kjh_ru_russian_khakas_done_clean.csv')
    kjh_sents = [x.strip() for x in df['kjh'].values.tolist()]

    ru_sents = df['Russian'].values.tolist()
    print(repr(kjh_sents[0]))
    print(repr(ru_sents[0]))
    print()

    with open('/home/adeshkin/khakas_projects/data/translation/little_prince/prince_kjh_ru_khakas_fixed.txt', 'w') as f:
        f.write('\n'.join(kjh_sents))

    with open('/home/adeshkin/khakas_projects/data/translation/little_prince/prince_kjh_ru_khakas_fixed.txt') as f:
        kjh_lines = f.readlines()

    assert len(kjh_lines) == len(kjh_sents)
    for sent1, sent2 in zip(kjh_lines, kjh_sents):
        assert sent1.strip() == sent2

    with open('/home/adeshkin/khakas_projects/data/translation/little_prince/prince_kjh_ru_russian.txt') as f:
        ru_lines = f.readlines()

    assert len(ru_lines) == len(ru_sents)
    for sent1, sent2 in zip(ru_lines, ru_sents):
        assert sent1 == sent2

    assert len(kjh_lines) == len(ru_lines)
    print(repr(kjh_lines[0]))
    print(repr(ru_lines[0]))
    print(repr(kjh_lines[-1]))
    print(repr(ru_lines[-1]))

    text = ' '.join(kjh_lines)
    print(repr(''.join(sorted(set(text)))))


if __name__ == '__main__':
    save_to_file()
