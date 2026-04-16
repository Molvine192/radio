# Dragon Radio — Minecraft Stream Server

Стриминг MP3 для мода Dragon's Radio в Minecraft 1.7.10.

## Структура

```
radio/
├── app.py
├── requirements.txt
├── render.yaml
├── .gitignore
└── tracks/
    └── your_track.mp3   ← сюда кидаешь треки
```

## Деплой на Render

1. Залей репозиторий на GitHub (публичный)
2. Зайди на [render.com](https://render.com) → New → Web Service
3. Подключи репозиторий
4. Render сам подхватит `render.yaml`
5. После деплоя зайди на сайт, скопируй ссылку трека
6. Вставь в Dragon's Radio в Minecraft

## URL стрима

```
https://твой-сервис.onrender.com/stream/название_трека.mp3
```

## Важно

- Треки кладёшь в папку `tracks/` и коммитишь в репозиторий
- Бесплатный Render засыпает после 15 мин неактивности — первое подключение может занять ~30 сек
- `--timeout 3600` в gunicorn нужен чтобы стрим не обрывался
