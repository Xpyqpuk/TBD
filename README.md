# RoadAccidentsProject
Шаг 1: настройка mysql
- выполняем bash script
- Добавляем строку /tmp/** rwk в /etc/apparmor.d/usr.sbin.mysqld
Для обновления конфигов может понадобится перезагрузка

Шаг 2: добавляем нового пользователя
Делаем sudo mysql, пишем:
GRANT ALL PRIVILEGES ON *.* TO 'DreamTeam'@'localhost' IDENTIFIED BY '1234';
CREATE DATABASE RoadAccidentsDB;

Шаг 3:
Скачиваем данные с кэгла https://www.kaggle.com/nichaoku/gbaccident0516, разахивируем в папку с проектом.
Запускаем скрипт fill_db.py. База наполнится автоматически.

Шаг 4:
Устанавливаем Django, запускаем проект.
Пример:
python3 ~/RoadAccident/manage.py runserver
В случае, если стандартные настройки не были изменены, то главнуй страницу сайта можно найти по адресу http://127.0.0.1:8000/MySite/
