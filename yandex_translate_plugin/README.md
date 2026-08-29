# Перевод через Yandex Translate (Chromium + remote debugging)

Перевод текстов **ru → kjh (хакасский)** через сайт `translate.yandex.com`, без API-ключа:
скрипт подключается по CDP (Chrome DevTools Protocol) к уже запущенному Chromium,
подставляет текст в поле ввода переводчика и читает результат из блока перевода.

## Файлы

- `yandex_translate_csv_ru_kjh.py` — основной скрипт: читает CSV, переводит колонку `ru`, пишет колонку `kjh`.

## Установка зависимостей

```bash
pip install pandas requests websocket-client
```

## Запуск

### 1. Запустить Chromium с включённым remote debugging

Обязательно отдельный `--user-data-dir`, иначе Chromium подключится к уже открытому
профилю и порт отладки не откроется:

```bash
chromium --remote-debugging-port=9222 --user-data-dir=/tmp/chromium-yandex --remote-allow-origins=*
```

Если команда `chromium` не найдена, используйте `chromium-browser`:

```bash
chromium-browser --remote-debugging-port=9222 --user-data-dir=/tmp/chromium-yandex --remote-allow-origins=*
```

Проверить, что порт отвечает:

```bash
curl -s http://127.0.0.1:9222/json/list | head
```

В открывшемся окне лучше один раз вручную зайти на
`https://translate.yandex.com/?source_lang=ru&target_lang=kjh` и убедиться, что
перевод работает и нет капчи. Окно браузера во время работы скрипта закрывать нельзя.

### 2. Запустить перевод

```bash
python yandex_translate_csv_ru_kjh.py /home/adeshkin/Downloads/ru_alpaca_seed_tasks_splitted.csv
```

Результат по умолчанию — `путь/к/файлу_kjh.csv`: все исходные колонки плюс новая колонка `kjh`.

### Опции

| Опция | Описание |
| --- | --- |
| `-o, --output` | путь к выходному CSV (по умолчанию `<input>_kjh.csv`) |
| `-c, --column` | имя колонки с русским текстом (по умолчанию `ru`) |
| `--port` | порт remote debugging Chromium (по умолчанию `9222`) |
| `--sleep` | пауза между запросами в секундах (по умолчанию `0.5`) |
| `--limit` | перевести только первые N строк (удобно для проверки) |
| `--resume` | продолжить прерванный перевод: пропустить строки, уже записанные в выходной файл |

Примеры:

```bash
python yandex_translate_csv_ru_kjh.py data/sents.csv -o data/sents_kjh.csv --sleep 1.0
```

```bash
python yandex_translate_csv_ru_kjh.py data/sents.csv --limit 10
```

```bash
python yandex_translate_csv_ru_kjh.py data/sents.csv --resume
```

## Как это работает

1. `create_target()` ищет среди вкладок браузера открытый переводчик с нужной парой языков,
   если такой вкладки нет — открывает её через `Target.createTarget`.
2. Для каждой строки очищается блок перевода (`#translation > span`), в поле ввода
   (`#fakeArea`) подставляется текст и посылается событие `input`.
3. Скрипт ждёт, пока перевод появится и перестанет меняться (Yandex дописывает текст
   по мере перевода), и забирает итоговое значение.
4. Каждая строка сразу дописывается в выходной CSV, поэтому при сбое прогресс не теряется —
   можно продолжить с `--resume`.

## Возможные проблемы

- **`Нет открытых вкладок в браузере на порту 9222`** — Chromium не запущен с `--remote-debugging-port`
  или использован тот же `--user-data-dir`, что и у обычного профиля.
- **`Handshake status 403 Forbidden ... --remote-allow-origins`** — Chrome/Chromium 111+ не принимает
  WebSocket-соединение с заголовком `Origin`. Скрипт этот заголовок не отправляет
  (`suppress_origin=True`), так что обычно ошибки нет; если она всё же появилась — обновите
  `websocket-client` (`pip install -U websocket-client`) и запускайте браузер с флагом
  `--remote-allow-origins=*`, как в команде выше.
- **Пустые переводы** — сайт мог показать капчу или изменить вёрстку. Загляните в окно браузера;
  при смене вёрстки поправьте селекторы `INPUT_SELECTOR` / `OUTPUT_SELECTOR` в начале скрипта.
- **Обрывы и ошибки соединения** — скрипт делает 3 попытки на строку с переподключением;
  при частых сбоях увеличьте `--sleep`.
