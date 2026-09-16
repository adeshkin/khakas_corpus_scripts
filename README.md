# Khakas corpus scripts

Набор Python-скриптов для сбора, очистки, подготовки и анализа хакасских и
хакасско-русских корпусов. Репозиторий объединяет как повторяемые пайплайны,
так и одноразовые исследовательские утилиты.

> [!IMPORTANT]
> У многих одноразовых скриптов пути к входным и выходным файлам указаны прямо
> в коде. Перед запуском найдите такие пути (`/home/...`, `/content/...`) и
> замените их на локальные. По возможности запускайте команды из корня
> репозитория — некоторые утилиты используют относительные пути.

## Быстрый старт

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Корневой `requirements.txt` содержит общие зависимости, но не является единым
окружением для всех исторических скриптов. У самостоятельных инструментов могут
быть дополнительные требования:

- `coregrammar_dataset/requirements.txt` — подготовка Core Grammar;
- `archive/legacy_scripts/requirements.txt` — архивные скрипты;
- `yandex_translate_plugin/README.md` — браузерный перевод через Yandex.

Перед первым запуском конкретного файла проверьте его импорты и блок
`if __name__ == "__main__"` в конце файла.

## Карта репозитория

### Основной рабочий процесс

| Каталог | Назначение |
| --- | --- |
| [`collect/`](collect/) | Скачивание корпусов, сбор Common Voice, определение языка, машинный перевод и публикация датасетов в Hugging Face. |
| [`clean/`](clean/) | Проверка алфавита и символов, нормализация и очистка монолингвальных текстов. |
| [`prepare/`](prepare/) | Подготовка таблиц и датасетов, разбиение на предложения и части, сбор результатов перевода. |
| [`merge_tables/`](merge_tables/) | Объединение и сверка CSV, Excel и параллельных текстов. |
| [`analysis/`](analysis/) | Статистика корпуса и диагностический анализ датасетов. |

Типичный поток данных:

```text
collect/ → clean/ или nllb_preprocess/ → prepare/ → merge_tables/ → analysis/
```

Это ориентир, а не единый автоматизированный пайплайн: большинство файлов
запускаются независимо.

### Самостоятельные пайплайны и наборы данных

| Каталог | Назначение |
| --- | --- |
| [`coregrammar_dataset/`](coregrammar_dataset/) | Воспроизводимая подготовка русских предложений для ручного перевода; есть [инструкция](coregrammar_dataset/README.md) и тесты. |
| [`nllb_preprocess/`](nllb_preprocess/) | Очистка, фильтрация, дедупликация и финализация корпуса в стиле NLLB; см. [описание пайплайна](nllb_preprocess/README.md). |
| [`gatitos_review/`](gatitos_review/) | Инструменты автоматической и ручной проверки переводов Gatitos. Локальные CSV и словари исключены из Git. |
| [`smol/`](smol/) | Подготовка и проверка наборов `gatitos`, `smoldoc` и `smolsent`. |
| [`external_datasets/`](external_datasets/) | Адаптация внешних наборов BOUQuET, WMT24++, Baby-MMLU и связанных экспериментов. |
| [`alpaca_kjh/`](alpaca_kjh/) | Подготовка русских Alpaca-инструкций к переводу на хакасский. |
| [`til_corpus/`](til_corpus/) | Загрузка монолингвальной и параллельной частей TIL Corpus. |
| [`yandex_translate_plugin/`](yandex_translate_plugin/) | Перевод CSV через веб-интерфейс Yandex Translate; см. [инструкцию](yandex_translate_plugin/README.md). |

### Вспомогательные материалы

| Каталог | Назначение |
| --- | --- |
| [`pdf/`](pdf/) | Нарезка PDF и переименование файлов. |
| [`parse_dict/`](parse_dict/) | Промпт для LLM-парсинга статей хакасского толкового словаря. |
| [`archive/legacy_scripts/`](archive/legacy_scripts/) | Старые версии и завершённые одноразовые скрипты; они сохранены для истории и не считаются поддерживаемыми. |

## Как найти нужный скрипт

- Скачать или опубликовать данные — `collect/`.
- Проверить символы и очистить текст — `clean/` или полный пайплайн
  `nllb_preprocess/`.
- Подготовить новую таблицу к переводу — `prepare/`.
- Объединить результаты нескольких источников — `merge_tables/`.
- Посчитать статистику или вручную проверить результат — `analysis/` либо
  тематический каталог набора данных.
- Найти старую реализацию — `archive/legacy_scripts/`.

## Запуск самостоятельных инструментов

Core Grammar:

```bash
python -m pip install -r coregrammar_dataset/requirements.txt
python coregrammar_dataset/prepare_coregrammar.py --help
```

Перевод CSV через Yandex:

```bash
python yandex_translate_plugin/yandex_translate_csv_ru_kjh.py --help
```

Выбор русских переводов для Gatitos:

```bash
python smol/gatitos/select_russian_translations.py --help
```

Остальные скрипты в основном не имеют общего CLI. Их параметры, пути и
вызываемые функции задаются в самих файлах.

## Проверки

Тесты воспроизводимого пайплайна Core Grammar не требуют сети:

```bash
python -m unittest discover -s coregrammar_dataset/tests -v
```

Для быстрой проверки синтаксиса всех актуальных Python-файлов:

```bash
python -m compileall \
  alpaca_kjh analysis clean collect coregrammar_dataset external_datasets \
  gatitos_review merge_tables nllb_preprocess pdf prepare smol til_corpus \
  yandex_translate_plugin
```

## Правила для новых файлов

1. Кладите скрипт в каталог этапа обработки или конкретного датасета, а не в
   корень репозитория.
2. Входные данные и крупные результаты храните вне Git; добавляйте локальные
   пути в `.gitignore`.
3. Для повторяемого инструмента используйте аргументы командной строки вместо
   захардкоженных путей и добавляйте короткий README в его каталог.
4. Устаревшие версии переносите в `archive/legacy_scripts/`, не смешивая их с
   рабочими файлами.

## Секреты и локальные данные

Файл `.env`, виртуальные окружения, IDE-настройки, кэши и локальные таблицы
Gatitos исключены через `.gitignore`. Не добавляйте в репозиторий API-ключи,
токены Hugging Face и персональные выгрузки.

## Лицензия

См. [`LICENSE`](LICENSE).
