import pandas as pd
pd.set_option('display.max_colwidth', None)
import re

def main():
    # df = pd.read_csv('/home/adeshkin/Downloads/khakas_50k_to_translate.tsv', sep='\t', header=None)
    df = pd.read_table('/home/adeshkin/Downloads/khakas_50k_to_translate.tsv', header=None)
    df = df.fillna('')
    kjh_ru_pairs = df[[0, 1]].values.tolist()

    df_src = pd.read_excel('/home/adeshkin/Downloads/khakas_50k_to_translate.xlsx')
    kjh_sents = df_src['kjh'].values.tolist()[:1800]
    idxs = []
    jdxs = []

    def clean_text(text):
        text = ' '.join(re.findall(r'[^\W\d_]+', text))
        text = re.sub(r'\\s+', ' ', text)

        return text.strip()

    kjh_ru_pairs1 = [(clean_text(x.lower()), y) for x, y in kjh_ru_pairs]
    for j, kjh_sent in enumerate(kjh_sents):
        kjh_sent = kjh_sent.lower()
        kjh_sent = clean_text(kjh_sent)
        for i, (kjh_pair, ru_pair) in enumerate(kjh_ru_pairs1):
            if kjh_sent in kjh_pair:
                idxs.append(i)
                jdxs.append(j)


    # kjh_sents = [item for idx, item in enumerate(kjh_sents) if idx not in jdxs]
    # print(kjh_sents)
    print(len(kjh_sents))
    print(len(jdxs))
    print(len(set(idxs)))
    print(len(kjh_ru_pairs))

    kjh_ru_pairs_final = [(item[0].strip(), item[1].strip()) for idx, item in enumerate(kjh_ru_pairs) if idx not in idxs and len(item[0]) >= 5 and len(item[1]) >= 1]
    print(len(kjh_ru_pairs_final))
    df = pd.DataFrame(kjh_ru_pairs_final, columns=['kjh', 'ru'])
    print(len(df))
    df = df[~df['kjh'].str.contains('\t')]
    print(len(df))
    df = df[~df['kjh'].str.contains('\n')]
    print(len(df))
    for i in range(0, len(df), 200):
        df[i:i + 200].to_csv(f'/home/adeshkin/Downloads/khakas_50k_to_translate_except_1800/{i:04d}.csv', index=False)





if __name__ == '__main__':
    main()
