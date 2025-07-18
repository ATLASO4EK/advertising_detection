# Городовёнок
![](https://img.shields.io/badge/Made_by-Рекламщики-yellow) ![](https://img.shields.io/badge/Forum-БММ2025-green) ![](https://img.shields.io/badge/Sponsored_by-НКЭиВТ-blue) ![](https://img.shields.io/badge/Employeer-SITRONICS-purple) 
> **Проект по автоматической детекции и классификации несанкционированной наружной рекламы, граффити или вывесок, не соответсвующих дизайн-коду города с использованием компьютерного зрения.**

## О проекте

Этот проект направлен на разработку системы, способной:
- Обнаруживать рекламные конструкции на изображениях
- Классифицировать их на легальные и несанкционированные
- Передавать данные через Telegram-бота в API-сервис для дальнейшей обработки
- Создавать запросы на урегулирование несанкционированного размещения рекламы, вывесок и граффити
---
Используемые методы: 
- YOLO для детекции объектов
- LLM для классификации по изображению и текстовому запросу с дизайн-кодом города
- (Потенциал для расширения) Использование авторских CNN для классификации в соответствии с дизайн-кодом города
- Flask API
- Aiogram 3.x Telegram-bot

## Актуальность

Несанкционированная наружная реклама и вывески — серьезная проблема городской среды:
- Портит эстетический вид улиц
- Портит историческое достояние города
- Нарушает законодательство
- Может быть опасной (непрочные конструкции)
- Увеличивает нагрузку на муниципальные службы

Система позволяет:
- Автоматизировать мониторинг городских территорий
- Сократить время реагирования инспекторов
- Повысить прозрачность и объективность контроля
- Ускорить обработку запросов на урегулирование случаев размещения несанкционированных информационных конструкций

## О нас
Мы команда энтузиастов и специалистов в области искусственного интеллекта и разработки ПО:
| Имя | GitHub | Роль | Задачи |
|-----|----|------|-------------------------|
| Дьячкова Алёна | [snow-faller](https://github.com/snow-faller "Дьячкова Алёна") | Project Manager, Developer | Оформление проекта, SQL-разработка |
| Христофорова Алёна | [Hao_pc](https://github.com/hao-pc "Христофорова Алёна") | Data Scientist, Developer | Docker, Data-аналитика, SQL-разработка |
| Кравченко Алексей | [atlaso4ek](https://github.com/ATLASO4EK "Кравченко Алексей") | sr. Developer | Обучение моделей, Telegram-боты, Flask API |
| Бикбаев Никита | [NiktWK](https://github.com/NiktWK "Бикбаев Никита") | sr. Developer | Telegram-боты, Flask API |
| Жеребцов Никита | [Vilk01](https://github.com/Vilk01 "Жеребцов Никита") | jr. Developer | Тестирование моделей |


## Документация пользователя

Для создания запроса на проверку санкционированности размещения информационных вывесок воспользуйтесь телеграмм-ботом по ссылке
[тык](https://t.me/ad_detection_bot)

Используйте /start для получения следующих инструкций
[![2025-07-17-15-53-27.png](https://i.postimg.cc/6qKgDs6D/2025-07-17-15-53-27.png)](https://postimg.cc/CBvcqQqN)

Отправьте свою геопозицию используя соответсвующую кнопку
[![2025-07-17-16-00-02.png](https://i.postimg.cc/j5ydHrk9/2025-07-17-16-00-02.png)](https://postimg.cc/5YNVJDJq)

Затем отправьте фото 
[![2025-07-17-16-42-15.png](https://i.postimg.cc/HnMmTXFF/2025-07-17-16-42-15.png)](https://postimg.cc/GTbVQ8Lj)

Будет создан запрос на проверку объекта
## Инструкция к запуску Docker Compose (Запуск сервера с API и Telegram-ботом)

### Перед запуском необходимо поменять порты. Во всех файлах с запросами к 127.0.0.1 поменять порт на 0.0.0.0, во всех файлах с запросами бота к API поменять на web (пример есть в ветке Alyona-H-branch)

Чтобы запустить Docker Compose, необходимо создать образы API и Telegram-бота.

Это можно сделать в директориях API и bot следующими командами соответственно:

#### docker build . -t app

#### docker build . -t bot

После успешного создания образов, можно перейти обратно в директорию src и создать и запустить контейнеры. Это делается с помощью команды:

#### docker compose up

(Чтобы проделать следующие процедуры, необходимо установить [Docker](https://www.docker.com/products/docker-desktop/), желательно на системы Unix-like)
