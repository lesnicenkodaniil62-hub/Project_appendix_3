# Название проекта

## Описание
На данный момент проект является учебным материалом и находица на являеца лишь альфа версией названия пока что нету но рабочие нозваниее пока если судить по условию задачи данного проекта является интернет магазин

## Установка

1. Клонируйте репозиторий:
```
git clone https://github.com/lesnicenkodaniil62-hub/Coursework-3
```
2. Установите зависимости:
```
На данный момент появилась библиотека requests и python-dotenv также в пректе теперь участвует библиотека os, dadataim, json, logging.
А такж используются линтер, статический анализатор и форматер кода. 
Для обработки и анализа данных в формате Excel я импртирокал библиотеку pandas.
А для чтения формата xlsx нужно в прект установить ещё и openpyxl.
Поскольку проект прошёл тестирование через pytest, у него есть зависимости — именно эти инструменты. Они указаны в файле pyproject.toml. 
А также теперьв тестирование участвует Mock и patch. На даный момет всё.
Если у вас они отсутствуют, вы можете установить их с помощью команд, приведённых ниже.
Была добавлена библиотека psycopg2 для совмещение с БД PostgreSQL
Была добавлена библиотека schedule для БД PostgreSQL для обновление таблици БД какждый час данные будут обновляца.
1. flake8 
poetry add --group lint flake8
2. mypy
poetry add --group lint mypy
3. black
poetry add --group lint black
4. isort
poetry add --group lint isort
5. psycopg2
poetry add --group lint psycopg2
6. schedule
poetry add schedule
7. requests
poetry add requests
8. pandas
poetry add pandas
9. openpyxl
poetry add openpyxl
10. python-dotenv
poetry add python-dotenv
11. pytest
poetry add --group dev pytest
Code coverage в
Code coverage в библиотеку pytest
poetry add --group dev pytest-cov

```
Более подробные настройки линтеров можно узнать тут, а также тесты, которые прошли функции можно узнать тут же [документации](docs/README.md).

## Использование:



## Документация:

Для получения дополнительной информации обратитесь к [документации](docs/README.md).

## Лицензия:

Этот проект лицензирован по [лицензии MIT](LICENSE).