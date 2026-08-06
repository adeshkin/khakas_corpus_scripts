import pandas as pd


def join_data(split):
    data_dir = f'/home/adeshkin/khakas_projects/data/translation/til_corpus/para/{split}/kjh-ru'
    k_path = f'{data_dir}/kjh-ru.kjh'
    r_path = f'{data_dir}/kjh-ru.ru'

    with open(k_path, 'r') as f:
        k_lines = f.readlines()

    with open(r_path, 'r') as f:
        r_lines = f.readlines()

    assert len(k_lines) == len(r_lines)

    return k_lines, r_lines


def main():
    all_k_lines, all_r_lines = [], []
    for split in ['dev', 'test', 'train']:
        k_lines, r_lines = join_data(split)
        all_k_lines.extend(k_lines)
        all_r_lines.extend(r_lines)

    assert len(all_k_lines) == len(all_r_lines)
    print(len(all_k_lines), len(all_r_lines))

    df = pd.DataFrame({'Хакасский': all_k_lines, 'Русский': all_r_lines})
    print(df.sample(10))

    df.to_csv('/home/adeshkin/khakas_projects/data/translation/til_corpus/para/til_para_corpus.csv', index=False)


if __name__ == '__main__':
    main()
