# Поиск схожих изображений

## Установка
```shell
$ git clone https://github.com/Klavionik/find_image.git
$ cd find_image
$ python -m venv venv && source venv/bin/activate
$ pip install -r requirements.txt
```

## Запуск
```shell
$ ./find_image.py {путь к файлу-образцу} {путь к начальной директории поиска}

# Например, если образец в одной папке со скриптом, а искать мы хотим на рабочем столе
$ ./find_image.py reference.jpg /home/user/Desktop
# Или если файл в другой папке, а искать хотим в той, где скрипт
$ ./find_image.py /home/user/Pictures/reference.jpg .
```