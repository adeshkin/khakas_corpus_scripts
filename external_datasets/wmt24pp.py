import datasets
import pandas as pd
import re
from razdel import sentenize


def get_word_count(text):
    word_count = len(re.findall(r'[^\W\d_]+', text))

    return word_count


def split_sent(text, max_words_per_chunk=12):
    sentences = [s.text for s in sentenize(text)]

    chunks = []
    buffer = []
    buffer_word_count = 0

    for sentence in sentences:
        word_count = get_word_count(sentence)

        if word_count >= max_words_per_chunk:
            if buffer:
                chunks.append(" ".join(buffer))
                buffer = []
                buffer_word_count = 0

            chunks.append(sentence)
        else:
            if buffer_word_count + word_count > max_words_per_chunk:
                chunks.append(" ".join(buffer))
                buffer = [sentence]
                buffer_word_count = word_count
            else:
                buffer.append(sentence)
                buffer_word_count += word_count

    if buffer:
        chunks.append(" ".join(buffer))

    return chunks


def main():
    data = datasets.load_dataset("google/wmt24pp", "en-ru_RU", split="train").to_pandas()
    data = data[~data['is_bad_source']]

    # data['target_sents'] = data['target'].apply(split_sent)
    # all_sents = []
    # for target_sents, segment_id in data[['target_sents', 'segment_id']].values.tolist():
    #     for i, target_sent in enumerate(target_sents):
    #         all_sents.append((target_sent, i, segment_id))

    # df = pd.DataFrame(all_sents, columns=['Русский', 'segment_id'])
    df = pd.DataFrame(data[['target', 'segment_id']].values.tolist(), columns=['Русский', 'segment_id'])
    print(len(df))
    df.drop_duplicates(subset='Русский', keep='first', inplace=True)
    print(len(df))
    for i in range(0, len(df), 200):
        df[i:i + 200].to_csv(f'./full_google_wmt24pp_{i:04d}.csv', index=False)


if __name__ == '__main__':
    main()
