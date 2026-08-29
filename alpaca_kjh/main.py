import json
from razdel import sentenize, tokenize
import pandas as pd

def get_sents(text, text_type, text_id):
    sents = []
    parts = text.split('\n')
    for p_id, part in enumerate(parts):
        part = part.strip()
        if len(part) == 0:
            continue
        num_words = len(list(tokenize(part)))
        if num_words > 15:
            for i, s in enumerate(sentenize(part)):
                sents.append((s.text, text_type, text_id, p_id, i))
        else:
            sents.append((part, text_type, text_id, p_id, 0))

    return sents



def main():
    all_sents = []
    with open("/home/adeshkin/Downloads/ru_alpaca_seed_tasks.jsonl", 'r', encoding='utf-8') as f:
        for j, line in enumerate(f):
            data = json.loads(line)
            sents = get_sents(data['instruction'], 'instruction', j)
            for inst in data['instances']:
                if len(inst['input']) > 0:
                    sents.extend(get_sents(inst['input'], 'instances_input', j))
                    # sents_input = [(s.text, 'instances_input', j, i) for i, s in enumerate(sentenize(inst['input']))]
                    # sents.extend(sents_input)
                if len(inst['output']) > 0:
                    sents.extend(get_sents(inst['output'], 'instances_output', j))
                    # sents_output = [(s.text, 'instances_output', j, i) for i, s in enumerate(sentenize(inst['output']))]
                    # sents.extend(sents_output)
            all_sents.extend(sents)

    df = pd.DataFrame(all_sents, columns=['ru', 'type', 'instruction_id', 'paragraph_id', 'sent_id'])
    df.to_csv('/home/adeshkin/Downloads/ru_alpaca_seed_tasks_splitted.csv', index=False)


if __name__ == '__main__':
    main()
