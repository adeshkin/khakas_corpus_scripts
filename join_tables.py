import pandas as pd


def main():
    df = pd.read_csv('/home/adeshkin/Downloads/bouquet_test_final - bouquet_test.csv')
    df = df.fillna('')
    examples = df[df['ru'] != df['src_text']][['ru', 'src_text', 'uniq_id']].values.tolist()
    for example in examples:

        if example[0].strip() != example[1].strip():
            print(example[0])
            print(example[1])
            print(example[2])
            print()

    good_ru_ids = ['P021-S3',
                   'P041-S2',
                   'P063-S2',
                   'P068-S1',
                   'P068-S2',
                   'P068-S3',
                   'P074-S4',
                   '',
                   '',
                   '',
                   '',
                   '',
                   '',
                   '',
                   '',
                   ]
    # <Обслуживание клиентов:> Здравствуйте! Приносим глубокие извинения за долгое ожидание.
    # Он показал такой класс, как будто герой Болливуда сначала попозировал, а потом ушёл.
    # Я ищу кого-то, кому можно доверять и кто любит кошек. Если вы знаете подходящего человека, то пожалуйста отправьте мне сообщение.

    #dev
    # good_ru_ids = ['P048-S1',#
    #                'P062-S2',#
    #                'P062-S3',#
    #                'P290-S3',
    #                'P398-S1',
    #                'P451-S3'
    #                ]

    # 'P417-S2'  P417-S4 P070-S2
    # Приёмная, в которую вошла Диана: - dev проверить


if __name__ == '__main__':
    main()
