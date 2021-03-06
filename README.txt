FTP-Client
##########

FTP-Client - ftp-клиент, написанный на Python

Состоит из модулей:
ftp.py - библиотека для общения с ftp-сервером
ftp_cui.py - консольный ftp-клиент, поддерживающий просмотр
директорий, скачивание файлов, загрузку файлов, как пофайловую,
так и рекурсивную.

Консольный FTP-клиент
#####################

Запуск консольного клиента:
python ftp_cui.py [-active] [-debug] [-host <host>] [-port <port>] [-user <username>]
Ключи:
--active          - включает активный режим работы клиента
--debug           - включает режим отладки
--host <host>     - указывает адрес хоста
--port <port>     - указывает порт для подключения
--user <username> - указывает имя пользователя

Поддерживаемые клиентом команды:
help
exit
quit
cd
ls
recv
cd
cdup
mkdir

    help [<command>]
Без параметров выводит список допустимых команд.
Если указать в качестве параметра <command> одну из допустимых
комманд, то выводит справку по ней.

    quit
    exit
Выход из программы.

    cd <pathname>
Меняет текущую удаленную директорию на <pathname>.

    ls [<pathname>]
    dir [<pathname>]
Без параметров выводит список файлов и каталогов в текущей
директории.
Если в качестве <pathname> указана директория, то выводит
спиоск файлов и каталогов в ней.

    put [-r] <filename0> [<filename1> ...]
Загружает файлы <filenameN> в текущую удаленную директорию.
Ключи:
-r  Позволяет загружать каталоги.

    recv [-r] <filename0> [<filename1> ...]
Скачивает файлы <filenameN> в текущую локальную директорию.
Ключи:
-r  Позволяет скачивать каталоги.

    cdup
Переход в родительскую удаленную директорию.

    mkdir <dirname>
Создает удаленный каталог <dirname>
