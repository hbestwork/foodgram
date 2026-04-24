![example workflow](https://github.com/hbestwork/foodgram/actions/workflows/main.yml/badge.svg)

Автор: Дмитрий Русановский

#  Проект Kittygram
Foodgram - это приложение, позволяющее пользователям обмениваться информацией о рецептах различных блюд.

## Стек технологий
- Python
- Django
- Node
- Docker
- PostgreSQL
- Nginx

## Как развернуть проект

- Создайте директорию для приложения, например, `foodgram/`
- Скопируйте туда файл `docker-compose.production.yml`
- Создайте в этой директории файл `.env`
- Заполните файл `.env`, как показано в следующей секции
- Запустите приложение командой `sudo docker compose -f docker-compose.production.yml up -d`
- Выполните команды:
  ```bash
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
  sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
  ```
  
## Как заполнить файл `.env`
Пример заполнения `.env` файла можно найти в файле `.env.example`
Параметры:
- `POSTGRES_DB` - Название базы данных (может быть любым, можно оставить как есть)
- `POSTGRES_USER` - Имя пользователя базы данных (может быть любым, можно оставить как есть)
- `POSTGRES_PASSWORD` - Пароль пользователя базы данных 
- `DB_HOST` - Адрес хоста, на котором находится база данных. Должно быть `db`.
- `DB_PORT` - Порт хоста, на котором находится база данных. Должно быть `5432`.
- `SECRET_KEY` - Секретный ключ.
- `DEBUG` - Отладочный режим приложения. В продакшене должно быть False.
- `ALLOWED_HOSTS` - Список доменных имён или хостов, для которых проект будет обслуживать запросы. Добавьте сюда адрес вашего удаленного сервера, при необходимости. 
- `PROD_DB` - Параметр, задающий использование в продакшене базы данных `PostgreSQL`. Должно быть True.