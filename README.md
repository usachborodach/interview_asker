# interview_asker

Сервис-«спрашиватель» вопросов для подготовки к собеседованиям.
Берёт случайный вопрос из локальных markdown-файлов и показывает ответ прямо в интерфейсе.

## Как это работает

- Вопросы и ответы лежат в директории `QANDA_DIR` (по умолчанию `/root/qanda/qanda`),
  по одному файлу на раздел: `main.md`, `base.md`, `docker.md`, …
- `main.md` — основной набор. Он питает `/`, `/api/random`, `/qanda`.
- Любой другой `<name>.md` автоматически доступен как раздел:
  - HTML-страница: `/<name>` (например, `/base`)
  - случайный вопрос: `/api/<name>/random`
  - JSON-выгрузка: `/qanda/<name>`
- Файлы кешируются в памяти процесса: перечитываются только при изменении
  `mtime` или размера. БД не используется.
- UI рендерит ответ инлайн (markdown → HTML через `marked.js` на клиенте).

Дополнительно есть отдельная страница `/Drewz1312-ml` — справочник по ML/RAG
из файла `ML_HANDBOOK_PATH`. В `/qanda` и `/qanda/<section>` его вопросы
**не попадают** — это независимый источник.

## Формат файла

Один файл — набор блоков, разделённых `\n\n---\n\n`:

```
# kubernetes. Что такое pod?
- под это объект, описывающий запуск контейнеров на ноде
- минимальная единица планирования

---

# kubernetes. Что такое Deployment?
- контроллер над ReplicaSet'ами
- умеет rolling update, rollback
```

- Вопрос — первая строка блока, начинающаяся с `#` (решётка и пробелы обрезаются).
- Ответ — всё остальное в блоке, в markdown.
- Блоки без `#` в первой строке игнорируются.

## Требования

- Python 3.10+

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

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `SECRET_KEY` | `dev-key-change-in-production` | секрет Flask |
| `QANDA_DIR` | `/root/qanda/qanda` | директория с `*.md` (main + разделы) |
| `ML_HANDBOOK_PATH` | `/root/ML-AI-Engineer-Interview-Handbook/ultimate_ml_rag_300_interview_handbook.md` | справочник для `/Drewz1312-ml` |

## Наполнение

Просто положите `.md`-файлы в `QANDA_DIR`. Основной — `main.md`.
Добавили `docker.md` — раздел сразу доступен по `/docker`, перезапуск не нужен:
первый запрос после правки перечитает файл по изменившемуся `mtime`.

Проверить из CLI:

```bash
flask --app wsgi list-sections           # перечислить все .md + число вопросов
flask --app wsgi count-questions         # main.md
flask --app wsgi count-questions base    # base.md
flask --app wsgi show-random             # случайный из main.md
flask --app wsgi show-random base        # случайный из base.md
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

`interview_asker.service` читает `.env` через `EnvironmentFile=/root/interview_asker/.env` —
`QANDA_DIR` и `ML_HANDBOOK_PATH` достаточно положить туда же.

Gunicorn запускает 2 воркера. У каждого свой кеш в памяти; при изменении
файла оба увидят новый `mtime` на первом же запросе после правки. Рестарт не нужен.

## HTTP API

| Метод | Путь | Что отдаёт |
|---|---|---|
| `GET` | `/` | HTML, вопросы из `main.md` |
| `GET` | `/api/random` | случайный из `main.md`: `{success, question, answer}` |
| `GET` | `/qanda` | все из `main.md`: `[{question, answer}, …]` |
| `GET` | `/<section>` | HTML-страница раздела (`<section>.md` должен существовать) |
| `GET` | `/api/<section>/random` | случайный вопрос из раздела |
| `GET` | `/qanda/<section>` | JSON раздела |
| `GET` | `/Drewz1312-ml` | HTML-страница ML/RAG-справочника |
| `GET` | `/api/ml/random` | случайный из ML/RAG-справочника: `{success, id, category, question, answer}` |

Пример:

```bash
curl -s https://interviewasker.usachborodach.ru/qanda | jq 'length'
# 340

curl -s https://interviewasker.usachborodach.ru/qanda/base | jq '.[0]'
# {"question": "kubernetes. Что такое Deployment?", "answer": "- контроллер..."}

curl -s https://interviewasker.usachborodach.ru/api/base/random | jq
# {"success": true, "question": "...", "answer": "..."}

curl -s https://interviewasker.usachborodach.ru/api/ml/random | jq
# {"success": true, "id": 42, "category": "RAG",
#  "question": "Как работает техника HyDE...", "answer": "1. ..."}
```

Порядок в `/qanda` и `/qanda/<section>` — как в файле. Формат `[{question, answer}, …]`
совпадает с тем, что раньше хранилось в Mongo — потребителям ничего менять не нужно.

## Роутинг: важное

- `/<section>` — единственный динамический шаблон. Он не перекрывает `/qanda`,
  `/Drewz1312-ml` и `/api/...` — Werkzeug отдаёт приоритет статическим сегментам.
- Имя раздела валидируется регуляркой `[A-Za-z0-9_-]+`, так что `../etc/passwd`
  и подобное отбивается с `404` ещё до любого обращения к файловой системе.
- Если `<section>.md` не существует — `404`.

## Запуск тестов

```bash
pytest -q
```

Тесты используют `tmp_path`; реальная директория и какая-либо БД не нужны.