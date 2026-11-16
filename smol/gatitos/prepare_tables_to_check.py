# import pandas as pd
# from glob import glob

# names = sorted(glob("/home/adeshkin/khakas_projects/gatitos_review/*01.csv"))

# for name1 in names:
#     name = name1.split('/')[-1].split('.')[0]
#     path = f"/home/adeshkin/khakas_projects/gatitos_review/{name}.csv"
#     df = pd.read_csv(path)
#     print(path)
#     fixes = pd.read_csv(f"/home/adeshkin/khakas_projects/gatitos_review/after_check/{name}-fix.csv")

#     start = int(name.split("-")[0])
#     df.index = pd.RangeIndex(start, len(df) + start, name="source_row")

#     columns = ["ru_recheck", "kjh_recheck"]
#     result = df.join(
#         fixes.set_index("source_row")[columns],
#         how="left",
#         validate="one_to_one",
#     )

#     result.to_csv(f"/home/adeshkin/Downloads/{name}-full-fix.csv", index=False, encoding="utf-8")

from pathlib import Path
import re

import pandas as pd

folder = Path("/home/adeshkin/Downloads")

files = sorted(
    (
        path
        for path in folder.glob("*.csv")
    ),
    key=lambda path: int(path.stem.split("-")[0]),
)
#print(files, sep='\n')

if not files:
    raise FileNotFoundError("Не найдены CSV с именами вида 1-300.csv")

result = pd.concat(
    [pd.read_csv(path) for path in files],
    ignore_index=True,
)

output = folder / "combined.csv"
result.to_csv(output, index=False, encoding="utf-8")

print("Порядок:", ", ".join(path.name for path in files))
print(f"Сохранено {len(result)} строк: {output}")