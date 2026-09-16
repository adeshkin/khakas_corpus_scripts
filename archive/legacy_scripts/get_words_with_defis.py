import pandas as pd
import re


def defis_dict_hrs_new34():
    data_dir = '/home/adeshkin/Desktop/defis_words'
    df = pd.read_csv(f'{data_dir}/hrs_new34_clean_4_col.csv')
    words = df['word'].tolist()
    all_defis_words = set()
    hyphenated_words = set()
    prefix_words = set()
    postfix_words = set()
    for word in words:
        word = word.lower().strip()
        if re.search(r'-', word):
            all_defis_words.add(word)

        if re.search(r'^\w+-\w+$', word):
            hyphenated_words.add(word)

        if re.search(r'^\w+-$', word):
            prefix_words.add(word)

        if re.search(r'^-\w+$', word):
            postfix_words.add(word)

    hyphenated_words.update(
        {'кирі-чимдік', 'тутхан-хапхан', 'апсах-иней', 'молат-чалат', 'илек-турах', 'сараат-хараат', 'ырғап-салғып',
         'чымыл-чымыл', 'успа-тӱспе'})
    print(all_defis_words.difference(hyphenated_words.union(prefix_words).union(postfix_words)))

    with open(f'{data_dir}/prefix_defis_words_dict_hrs_new34.txt', 'w') as f:
        for word in sorted(prefix_words):
            f.write(f'{word}\n')

    with open(f'{data_dir}/postfix_defis_words_dict_hrs_new34.txt', 'w') as f:
        for word in sorted(postfix_words):
            f.write(f'{word}\n')

    with open(f'{data_dir}/defis_words_dict_hrs_new34.txt', 'w') as f:
        for word in sorted(hyphenated_words):
            f.write(f'{word}\n')


def defis_uchebniki():
    data_dir = '/home/adeshkin/Desktop/defis_words'
    path = f'{data_dir}/uchebniki_docx_все_хак символы.txt'
    with open(path) as f:
        text = f.read()

    print(repr(''.join(sorted(set(text)))), '\n')
    assert 'ІіҒғҢңҶҷӦӧӰӱ' == 'ІіҒғҢңҶҷӦӧӰӱ'

    hyphenated_words = sorted(set(re.findall(r'\b\w+-\w+\b', text.lower())))
    print(len(hyphenated_words))
    with open(f'{data_dir}/defis_words_uchebniki_docx.txt', 'w') as f:
        for word in hyphenated_words:
            f.write(f'{word}\n')


if __name__ == '__main__':
    defis_dict_hrs_new34()
    defis_uchebniki()
