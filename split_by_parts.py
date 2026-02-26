import pandas as pd


def main():
    resampled_df = pd.read_csv('/home/adeshkin/Downloads/Шулбаева В_Чоохтар_clean.csv')
    # resampled_df = df.sample(frac=1).reset_index(drop=True)
    # assert len(df) == len(resampled_df)

    for i in range(0, len(resampled_df), 200):
        resampled_df[i:i + 200].to_csv(f'/home/adeshkin/Downloads/Шулбаева В_Чоохтар_{i:04d}.csv', index=False)

if __name__ == '__main__':
    main()