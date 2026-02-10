import pandas as pd
from glob import glob

def main():
    data_dir = '/home/adeshkin/Desktop/uchebniki_docx'
    paths = sorted(glob(f'{data_dir}/*/*_cl.txt'))
    sents = []
    for path in paths:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [x.strip() for x in f.readlines()[1:-1]]
        sents.extend(lines)

    for i in range(0, len(sents), 200):
        df = pd.DataFrame(sents[i:i+200], columns=['kjh'])
        df.to_csv(f'{data_dir}/tables/{i}.csv', index=False)



if __name__ == '__main__':
    main()