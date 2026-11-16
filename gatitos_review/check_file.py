import pandas as pd

df = pd.read_json('/home/adeshkin/Downloads/kjh_ru.jsonl', lines=True)

print(df.sample(10))