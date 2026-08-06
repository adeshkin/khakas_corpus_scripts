import os
from glob import glob

data_dir = '/home/adeshkin/Downloads/2'
names = os.listdir(data_dir)
for name in names:
    idx = int(name.split('-')[1])
    new_idx = idx + 25_000
    new_name = name.replace(f'-{idx}-', f'-{new_idx}-fix-')
    print(name)
    print(new_name)
    print()
    os.rename(os.path.join(data_dir, name), os.path.join(data_dir, new_name))