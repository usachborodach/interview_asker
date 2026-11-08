# interview_asker

Сервис-«спрашиватель» вопросов для подготовки к собеседованиям.
Берёт случайный вопрос из MongoDB и показывает ответ прямо в интерфейсе.

## Как это работает

- Вопросы и ответы хранятся в MongoDB: `interview_asker.qanda`, документы вида `{question, answer}`.
- Наполняется коллекция скриптом `update_qanda.py` (вне этого репозитория) — он парсит `qanda.md` и делает `insert_many`.
- Flask-приложение читает документы из Mongo и по запросу `/api/random` отдаёт случайный.
- UI рендерит ответ инлайн (markdown → HTML через `marked.js` на клиенте).

## Требования

- Python 3.10+
- MongoDB (локально или доступный по сети)

## Установка

```bash
apt install python3.10-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
```

## Конфигурация `.env`

```bash
cp .env.example .env
```

Сгенерировать `SECRET_KEY`:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Переменные:

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `SECRET_KEY` | `dev-key-change-in-production` | секрет Flask |
| `MONGO_URI` | `mongodb://localhost:27017` | строка подключения к Mongo |
| `MONGO_DB` | `interview_asker` | имя базы |
| `MONGO_COLLECTION` | `qanda` | коллекция с вопросами |

Если Mongo доступна не напрямую (например, на удалённом хосте через SSH-туннель), можно:

- поднять туннель и оставить `mongodb://localhost:27017`;
- либо прописать прямой `mongodb://user:pass@host:27017/?authSource=admin`.

## Наполнение базы

Вопросы заливаются `update_qanda.py` (лежит рядом с проектом):

```bash
python update_qanda.py
```

Скрипт:

- читает `qanda.md`, разбивает по `\n\n---\n\n`;
- обновляет JSON-ассет в Android-проекте (`interview_asker_android/.../qanda.json`);
- открывает SSH-туннель, подключается к Mongo, делает `delete_many({})` + `insert_many(...)`.

То есть коллекция **полностью перезаписывается** — это нормально, вопросы статические.

Проверить, что вопросы на месте:

```bash
flask --app wsgi count-questions
flask --app wsgi show-random
```

## Локальный запуск

```bash
python run.py    # http://0.0.0.0:8005
```

## Продакшен (systemd + nginx + gunicorn)

```bash
mkdir -p /var/log/interview_asker

ln -sf \
  /root/interview_asker/deploy/interview_asker.service \
  /etc/systemd/system/interview_asker.service
systemctl daemon-reload
systemctl enable --now interview_asker

ln -sf \
  /root/interview_asker/deploy/nginx.conf \
  /etc/nginx/sites-enabled/interview_asker
nginx -t && systemctl restart nginx

# logrotate
ln -sf /root/interview_asker/deploy/interview_asker.logrotate \
       /etc/logrotate.d/interview_asker
```

`interview_asker.service` читает `.env` через `EnvironmentFile=/root/interview_asker/.env` — `MONGO_URI` достаточно положить туда же.

## CLI-команды

```bash
flask --app wsgi count-questions   # сколько вопросов в Mongo
flask --app wsgi show-random       # показать случайный вопрос и ответ
```

## Запуск тестов

Тесты используют `mongomock` — реальная Mongo не нужна.

```bash
pytest -q
```

## HTTP API

| Метод | Путь | Что отдаёт |
|---|---|---|
| `GET` | `/` | HTML-страница с кнопками |
| `GET` | `/api/random` | один случайный вопрос: `{success, id, question, answer}` |
| `GET` | `/qanda` | все пары без `_id`: `[{question, answer}, ...]` |
| `GET` | `/Drewz1312-ml` | HTML-страница ML/RAG-справочника |
| `GET` | `/api/ml/random` | случайный вопрос из ML/RAG-файла: `{success, id, category, question, answer}` |

Пример:

```bash
curl -s https://interviewasker.usachborodach.ru/qanda | jq 'length'
# 340

curl -s https://interviewasker.usachborodach.ru/api/random | jq
# {
#   "success": true,
#   "id": "6543a…",
#   "question": "Что такое inode?",
#   "answer": "- Inode — структура метаданных файла…"
# }
```

`/qanda` отдаёт массив в порядке `qanda.md` (сортировка по `_id`) — формат совпадает с `qanda.json`, который `update_qanda.py` кладёт в Android-проект.


## ML/RAG справочник (`/Drewz1312-ml`)

Отдельная страница со случайными вопросами из markdown-файла
`ultimate_ml_rag_300_interview_handbook.md`. Источник — файл на хосте,
путь задаётся через `ML_HANDBOOK_PATH` (по умолчанию
`/root/ML-AI-Engineer-Interview-Handbook/ultimate_ml_rag_300_interview_handbook.md`).

Файл **не хранится в репозитории** — его нужно положить на сервер отдельно.
В отличие от `/qanda`, эти вопросы в JSON-выгрузку `/qanda` **не попадают**.

Формат файла, который парсится:

```
### [Категория] N. Текст вопроса
Текст ответа…
```

Всё до первого такого заголовка (интро, `# …`) игнорируется. Хвостовые `---`
между секциями от ответов отрезаются.

Файл кешируется в памяти процесса: перечитывается только при изменении
`mtime`. Проверка:

```bash
flask --app wsgi count-ml-questions
flask --app wsgi show-ml-random
```