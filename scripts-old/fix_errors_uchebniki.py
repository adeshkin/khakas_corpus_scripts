import re
import random


def prepare_defis_words():
    data_dir = '/home/adeshkin/Desktop/defis_words'
    with open(f'{data_dir}/prefix_defis_words_dict_hrs_new34.txt') as f:
        prefix_words = [x.strip().replace('-', '').lower() for x in f.readlines()]

    with open(f'{data_dir}/postfix_defis_words_dict_hrs_new34.txt') as f:
        postfix_words = [x.strip().replace('-', '').lower() for x in f.readlines()]

    with open(f'{data_dir}/defis_words_dict_hrs_new34.txt') as f:
        defis_words = [x.strip().lower() for x in f.readlines()]

    with open(f'{data_dir}/defis_words_uchebniki_docx.txt') as f:
        defis_words.extend([x.strip().lower() for x in f.readlines()])

    with open(f'{data_dir}/defis_words_custom.txt') as f:
        defis_words.extend([x.strip().lower() for x in f.readlines()])

    defis_words_new = []
    for d_word in defis_words:
        assert len(d_word.split('-')) == 2
        first_part = d_word.split('-')[0]
        second_part = d_word.split('-')[1]
        defis_words_new.append(f'{first_part}-{second_part[:4]}')

    return set(defis_words), set(defis_words_new), set(prefix_words), set(postfix_words)


def main():
    data_dir = '/home/adeshkin/Desktop/defis_words'
    path = f'{data_dir}/uchebniki_docx_все_хак символы.txt'
    # ІіҒғҢңҶҷӦӧӰӱ
    chisla = ['пір', 'ікі', 'ӱс', 'тӧрт', 'пис', 'алты', 'читі', 'сигіс', 'тоғыс', 'он']
    with open(path) as f:
        text = f.read()  # print(repr(''.join(sorted(set(text)))), '\n')
    text = re.sub('-\n', '- ', text)
    text = re.sub('\xad ', '- ', text)
    text = re.sub('\xad', '- ', text)  # re.findall(r'.{0,15}' + re.escape('\xad') + r'.{0,15}', text)

    defis_words, defis_words_short, prefix_words, postfix_words = prepare_defis_words()
    words = sorted(set(re.findall(r'(\w+)- (\w+)', text)))

    count = 0
    for word in words:
        first_part = word[0]
        second_part = word[1]
        if first_part.lower() == 'Чир'.lower() and 'суу' in second_part.lower():
            continue

        if first_part.lower() == 'оол'.lower() and 'хыс' in second_part.lower():
            continue

        if first_part.lower() in chisla and second_part.lower() in chisla:
            continue

        if first_part.lower() in prefix_words:
            continue

        if second_part.lower() in postfix_words:
            continue

        if first_part.lower() == second_part.lower():
            continue

        if first_part[-1].isupper() and second_part[0].islower():
            continue

        if first_part[-1].islower() and second_part[0].isupper():
            continue

        if first_part.isdigit():
            continue

        word1 = f'{first_part}-{second_part}'.lower()
        if word1 in defis_words:
            continue

        word2 = f'{first_part}-{second_part[:4]}'.lower()
        if word2 in defis_words_short:
            continue

        word3 = f'{second_part}-{first_part}'.lower()
        if word3 in defis_words:
            continue

        text = text.replace(f'{first_part}- {second_part}', f'{first_part}{second_part}')

        # if first_part[-4:].lower() == second_part[-4:].lower():
        #     print(word1)
        #     print(word)
        #     print()
        #     continue



        # if second_part in ['да', 'де']:
        #     if 'кем' in first_part.lower():
        #         print(word)
        #         continue
        count += 1

    print(len(words))
    print(count)
    words = sorted(set(re.findall(r'(\w+)- (\w+)', text)))

    print(*random.choices(words, k=10), sep='\n')
    print(len(words))

    for word in words:
        first_part = word[0]
        second_part = word[1]
        text = text.replace(f'{first_part}- {second_part}', f'{first_part}-{second_part}')


    with open(f'{data_dir}/uchebniki_docx_все_хак символы_defis_norm.txt', 'w', encoding='utf-8') as f:
        f.write(text)


if __name__ == '__main__':
    main()
