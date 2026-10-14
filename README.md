# interview_asker# Interview Asker

Сервис-«спрашиватель» вопросов для подготовки к собеседованиям.
Читает `list.md`, отдаёт случайный вопрос и открывает ответ на GitHub.

## Установка

```bash
apt install python3.10-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
```

## Конфигурация `.env`

```
cp .env.example .env
```

```bash
# SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Положите рядом с проектом файл `list.md` (тот же, что использует CLI-скрипт `interview_asker.py`):

```
/root/interview_asker/list.md
```

## Локальный запуск

```bash
flask --app wsgi list-questions   # проверить, что вопросы парсятся
python run.py                     # http://0.0.0.0:8005
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

## Запуск тестов

```bash
pytest -q
```