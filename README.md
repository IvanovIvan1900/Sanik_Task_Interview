# Sanik_Task_Interview
Проект разрабатывается как решение задачи с работодателя
https://docs.google.com/document/d/1lblqae9k0wdV7q7QFjxYcC_rrDbRb5DIUHtHiKM5iz4/edit
или файл Тестовое PythonМодель базы данных Пользователь – репрезентация пользователей в приложении. Должны быть обычные и админ поль.pdf.
При выполнении данного задания были использованы следующие технологии:
- Веб сервер        - Sanic
- Валидация данных  - pydantic
- Базы данных       - gino, alembic, postgres
- Тестирование      - pytest
При написании задания были созданы 53 теста.
Так же была сгенерирована документация для OpenAPI (Swagger)

Т.к. данный проект разрабатывается как "тестовое" задание в нем есть несколько допущений:
1. Вместо использования готовой библиотеки jwt, используется самописный костыль.
2. Конфигурация храниться неспосредственно в коде, хотя для этих целей лучше использовать другие механизмы:
    - yaml
    - Переменные окружения
    - Docker secrets
    и др.
3. Большинство view не тестировались на недопустимые методы, необходимость авторизации или необходимость административного доступа, хотя этот функционал для каждого из методов был реализован, и на выборочно - протестирован.

