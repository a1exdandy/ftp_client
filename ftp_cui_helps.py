__author__ = 'Kovrizhnykh Alexey'

UNKNOWN_COMMAND = """error: unknown command
try help
"""

HELP_MSG = """help
exit
quit
cd
ls
recv
cd
cdup
mkdir
help <command> for more info
"""

HELP_HELP = """    help [<command>]

Без параметров выводит список допустимых команд.
Если указать в качестве параметра <command> одну из допустимых
комманд то выводит справку по ней.
"""

QUIT_HELP = """    quit
    exit
Выход из программы.
"""

CD_HELP = """    cd <pathname>
Меняет текущую удаленную директорию на <pathname>.
"""

LS_HELP = """    ls [<pathname>]
    dir [<pathname>]
Без параметров выводит список файлов и каталогов в текущей
директории.
Если в качестве <pathname> указана директория, то выводит
спиоск файлов и каталогов в ней.
"""

PUT_HELP = """    put [-r] <filename0> [<filename1> ...]
Загружает файлы <filenameN> в текущую удаленную директорию.
Ключи:
-r  Позволяет загружать каталоги.
"""

RECV_HELP = """    recv [-r] <filename0> [<filename1> ...]
Скачивает файлы <filenameN> в текущую локальную директорию.
Ключи:
-r  Позволяет скачивать каталоги.
"""

CDUP_HELP = """    cdup
Переход в родительскую удаленную директорию.
"""

MKDIR_HELP = """    mkdir <dirname>
Создает удаленный каталог <dirname>
"""
