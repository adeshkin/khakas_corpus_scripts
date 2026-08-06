import pandas as pd


def main():
    resampled_df = pd.read_excel('/home/adeshkin/Downloads/khakas_50k_to_translate.xlsx', sheet_name='Sheet1')
    # # resampled_df = df.sample(frac=1).reset_index(drop=True)
    # # assert len(df) == len(resampled_df)
    #
    for i in range(0, 10000, 200):
        resampled_df[i:i + 200].to_csv(f'/home/adeshkin/Downloads/khakas_50k_to_translate_first_10k/{i:04d}.csv', index=False)

if __name__ == '__main__':
    main()