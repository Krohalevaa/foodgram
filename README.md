## CI/CD Badge 
[![Main Foodgram workflow](https://github.com/Krohalevaa/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/Krohalevaa/foodgram/actions/workflows/main.yml)

# Foodgram - Продуктовый помощник

«Foodgram» — онлайн-сервис для публикации рецептов. Пользователи могут создавать рецепты, добавлять их в избранное, подписываться на авторов и формировать список покупок.

## Особенности
- Просмотр рецептов с пагинацией
- Регистрация/аутентификация
- Добавление в избранное
- Список покупок с экспортом
- Подписки на авторов
- Создание/редактирование рецептов
- Деплой через Docker + CI/CD

## Технологии
- **Backend**: Django 4.2 + DRF
- **Frontend**: React
- **БД**: PostgreSQL
- **Инфраструктура**: Docker, Nginx
- **CI/CD**: GitHub Actions

---

## Установка и запуск

### Предварительные требования
- Docker 20.10+
- Docker Compose 1.29+

### Клонирование репозитория
```bash
git clone https://github.com/krohalevaa/foodgram.git
cd foodgram
```

### Настройка окружения
Создайте файлы окружения (backend/.env):
- SECRET_KEY=your-django-secret-key
- DEBUG=False
- DB_ENGINE=django.db.backends.postgresql
- DB_NAME=postgres
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=postgres
- DB_HOST=db
- DB_PORT=5432

### Запуск проекта
```bash
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --no-input
docker compose exec backend python manage.py createsuperuser
```

### Замены для настройки:
1. `yourusername` в URL репозитория
2. `your-dockerhub` в тегах образов
3. `your-server-ip` в секции доступа
4. Добавьте credentials в GitHub Secrets:
   - `SSH_HOST`
   - `SSH_USERNAME`
   - `SSH_KEY`

### Проект доступен по адресу:
- https://foodgram-net.hopto.org
- Админ: https://foodgram-net.hopto.org/admin/

### IP 
89.169.161.149;

### Админ учетка:
Логин: admin@gmail.com
Пароль: admin_yandex1

### Авторы

- Крохалева Анна - разработка

