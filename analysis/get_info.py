def main():
    data_dir = '/home/adeshkin/khakas_projects/data/translation/til_corpus'
    path = f'{data_dir}/mono/kjh.txt'
    with open(path, 'r') as f:
        data_mono = [x.strip() for x in f.readlines()]

    data_para = []
    for split in ['train', 'dev', 'test']:
        path = f'{data_dir}/para/{split}/kjh-ru/kjh-ru.kjh'
        with open(path, 'r') as f:
            data_para.extend([x.strip() for x in f.readlines()])

    data_para = set(data_para)
    assert len(data_mono) == len(set(data_mono))
    data_mono_new = []
    for sent in data_mono:
        if sent not in data_para:
            data_mono_new.append(sent)

    print(len(data_mono_new))

if __name__ == '__main__':
    main()
