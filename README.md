# Поиск схожих изображений

Скрипт для поиска похожих изображений. Внутри работает библиотека **imagehash**, использующая 
алгоритм перцептуального хэширования с использованием DCT (discrete cosine transform).

## Установка
Для работы скрипта нужен Python версии 3.7 или выше.

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

## Опции
### -d - расстояние Хэмминга (по умолчанию 0)
Максимальное расстояние Хэмминга при сравнении хэшей можно указать с помощью ключа `-d` или `--distance`.

```shell
# Максимальная разница между хэшами - 5 битов
$ ./find_image.py -d 5 reference/jpg .
```

### -s - чувствительность хэширования (по умолчанию 7)
Число от 2 до 8, определяющее параметр hash_size для алгоритма хэширования, задается ключом `-s` или `--sensitivity`.  
Цитата: **Increasing the hash size allows an algorithm to store more detail in its hash, increasing its sensitivity to changes in detail.**

```shell
$ ./find_image.py -s 6 reference.jpg .
```

### -e - список директорий, которые будут исключены из поиска
С помощью ключа `-e` или `--exclude` можно задать через запятую список имен директорий, файлы в которых будут пропущены при поиске.  

```shell
# Папки с именами "skipme" и "excludethis" будут пропущены
$ ./find_image.py -e skipme,excludethis reference.jpg .
```