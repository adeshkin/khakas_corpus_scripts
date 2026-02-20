import datasets
import pandas as pd

def main():
    data = datasets.load_dataset("facebook/bouquet", "sentence_level", split="dev").to_pandas()
    data_para = datasets.load_dataset("facebook/bouquet", "paragraph_level", split="dev").to_pandas()

    eng2rus = pd.merge(
        data.loc[data["src_lang"].eq("eng_Latn")].drop(["tgt_lang", "tgt_text"], axis=1),
        data.loc[data["src_lang"].eq("rus_Cyrl"), ["src_lang", "src_text", "uniq_id"]].rename({"src_lang": "tgt_lang", "src_text": "tgt_text"}, axis=1),
        on="uniq_id",
    )

    eng2rus_para = pd.merge(
        data_para.loc[data_para["src_lang"].eq("eng_Latn")].drop(["tgt_lang", "tgt_text"], axis=1),
        data_para.loc[data_para["src_lang"].eq("rus_Cyrl"), ["src_lang", "src_text", "uniq_id"]].rename({"src_lang": "tgt_lang", "src_text": "tgt_text"}, axis=1),
        on="uniq_id",
    )

    results = []
    for uniq_id in eng2rus_para['uniq_id']:
        # print(uniq_id)
        # src_text = eng2rus_para.loc[eng2rus_para['uniq_id'].eq(uniq_id)]['src_text'].values
        # tgt_text = eng2rus_para.loc[eng2rus_para['uniq_id'].eq(uniq_id)]['tgt_text'].values
        # assert len(src_text) == 1
        # assert len(tgt_text) == 1
        # results.append([src_text[0], '' ,tgt_text[0], uniq_id])

        uniq_id_sents = eng2rus.loc[eng2rus['uniq_id'].str.contains(uniq_id)]['uniq_id'].values
        src_sents = eng2rus.loc[eng2rus['uniq_id'].str.contains(uniq_id)]['src_text'].values
        tgt_sents = eng2rus.loc[eng2rus['uniq_id'].str.contains(uniq_id)]['tgt_text'].values
        assert len(src_sents) == len(tgt_sents)
        assert len(src_sents) == len(uniq_id_sents)
        for i in range(len(src_sents)):
            results.append([tgt_sents[i], '', src_sents[i], uniq_id_sents[i]])
        results.append(['', '', '', ''])
        results.append(['', '', '', ''])

    df = pd.DataFrame(results, columns=['Русский', 'Хакасский', 'Английский', 'Номер'])
    df.head()

    df.to_csv('/content/drive/MyDrive/проект по переводу хакниияли 2025/bouquet/dev_data.csv', index=None)


