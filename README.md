# mnh

Удаление данных
docker-compose down -v 
или
docker-compose down
docker volume rm -f $(docker volume ls -q)

Создание баз данных при остановленных контейнерах
docker-compose run web python manage.py makemigrations blog
docker-compose run web python manage.py migrate

Войти в django shell на запущеном контейнере
docker-compose exec web python manage.py shell
