import pandas as pd
from razdel import sentenize
import os
from glob import glob


def adaptive_chunking(text, max_words_per_chunk=10):
    # 1. Получаем список предложений
    sentences = [s.text for s in sentenize(text)]

    chunks = []
    buffer = []
    buffer_word_count = 0

    for sentence in sentences:
        # Считаем количество слов в текущем предложении (грубый подсчет по пробелам)
        # Для хакасского это работает нормально
        word_count = len(sentence.split())

        # СЦЕНАРИЙ А: Предложение само по себе огромное
        if word_count >= max_words_per_chunk:
            # Сначала сбрасываем то, что накопилось в буфере (мелочь)
            if buffer:
                chunks.append(" ".join(buffer))
                buffer = []
                buffer_word_count = 0

            # Добавляем большое предложение как отдельный кусок
            chunks.append(sentence)

        # СЦЕНАРИЙ Б: Предложение небольшое
        else:
            # Проверяем, влезет ли оно в текущий буфер
            if buffer_word_count + word_count > max_words_per_chunk:
                # Если перебор — сохраняем старый буфер и начинаем новый
                chunks.append(" ".join(buffer))
                buffer = [sentence]
                buffer_word_count = word_count
            else:
                # Если место есть — добавляем
                buffer.append(sentence)
                buffer_word_count += word_count

    # Не забываем остатки в конце текста
    if buffer:
        chunks.append(" ".join(buffer))

    return chunks


def main():
    data_dir = '/home/adeshkin/khakas_projects/data/mono'
    paths = sorted(glob(os.path.join(data_dir, '*.txt')))
    texts = []
    for path in paths:
        with open(path, 'r') as f:
            text = f.read()
        texts.append(text)
    all_text = '\n\n\n#####\n\n\n'.join(texts)
    all_text = all_text.replace('\n', ' ').replace('#####', ' ')

    chunks = adaptive_chunking(all_text)

    df = pd.DataFrame(chunks, columns=['Хакасский'])
    print(len(df))
    df.to_csv(f'{data_dir}/mono.csv', index=False)


if __name__ == '__main__':
    main()
