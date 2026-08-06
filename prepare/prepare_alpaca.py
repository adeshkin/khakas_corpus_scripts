import json
import os

import pandas as pd


def main():
    input_examples = set()
    output_examples = set()
    instructions = set()
    with open("/home/adeshkin/Downloads/ru_alpaca_seed_tasks/ru_alpaca_seed_tasks.jsonl", 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            instructions.add(data['instruction'])
            for inst in data['instances']:
                input_examples.add(inst['input'])
                output_examples.add(inst['output'])

    input_text = '\n'.join(input_examples)
    output_text = '\n'.join(output_examples)
    instructions_text = '\n'.join(instructions)
    with open('/home/adeshkin/Downloads/ru_alpaca_seed_tasks/input_instances.txt', 'w', encoding='utf-8') as f:
        f.write(input_text)
    with open('/home/adeshkin/Downloads/ru_alpaca_seed_tasks/output_instances.txt', 'w', encoding='utf-8') as f:
        f.write(output_text)

    with open('/home/adeshkin/Downloads/ru_alpaca_seed_tasks/instructions.txt', 'w', encoding='utf-8') as f:
        f.write(instructions_text)


def prepare_tables():
    data_dir = '/home/adeshkin/Downloads/ru_alpaca_seed_tasks'
    names = ['input_instances - input_instances.csv', 'output_instances - output_instances.csv',
             'instructions - instructions.csv']
    examples = []
    for name in names:
        path = os.path.join(data_dir, name)
        df = pd.read_csv(path)
        examples.extend(df[['Русский', 'Источник']].values.tolist())

    df = pd.DataFrame(examples, columns=['Русский', 'Источник'])
    for i in range(0, len(df), 200):
        df[i:i + 200].to_csv(f'{data_dir}/ru_alpaca_seed_tasks_{i:04d}.csv', index=False)


if __name__ == "__main__":
    prepare_tables()
