import pandas as pd 

path = '/home/adeshkin/Downloads/Copy of combined - combined.csv'
df = pd.read_csv(path)

row_clean = df['kjh_correct'].fillna('').astype(str).str.strip()
row_clean = df['ru_correct'].fillna('').astype(str).str.strip()
# # Задаем оба условия: длина < 2 символов И количество слов < 2
cond_length = row_clean.str.len() < 2

short_rows = df[cond_length]

short_rows.to_csv('/home/adeshkin/Downloads/Copy_of_combined_kjh_short.csv')
# 'm 
# ’m s re 