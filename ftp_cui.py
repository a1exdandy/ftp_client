__author__ = 'Kovrizhnykh Alexey'


import ftp
import os
import getpass
import argparse
import ftp_cui_helps as helps


class FtpCui:

    def __init__(self):
        self.handlers = {
            'help': self.help_handler,
            'quit': self.quit_handler,
            'exit': self.quit_handler,
            'cd': self.cd_handler,
            'ls': self.ls_handler,
            'dir': self.ls_handler,
            'put': self.put_handler,
            'recv': self.recv_handler,
            'cdup': self.cdup_handler,
            'mkdir': self.mkdir_handler
        }

        self.helps = {
            'help': helps.HELP_HELP,
            'quit': helps.QUIT_HELP,
            'exit': helps.QUIT_HELP,
            'cd': helps.CD_HELP,
            'ls': helps.LS_HELP,
            'dir': helps.LS_HELP,
            'put': helps.PUT_HELP,
            'recv': helps.RECV_HELP,
            'cdup': helps.CDUP_HELP,
            'mkdir': helps.MKDIR_HELP
        }

        self.client = None

    def run(self):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--active', action='store_true',
                                help='включает активный режим работы клиента')
        arg_parser.add_argument('--debug', action='store_true',
                                help='включает режим отладки')
        arg_parser.add_argument('--host', metavar='<host>', type=str,
                                help='указывает адрес хоста')
        arg_parser.add_argument('--port', metavar='<port>', type=int,
                                help='указывает порт')
        arg_parser.add_argument('--user', metavar='<user>', type=str,
                                help='указывает имя пользователя')
        args = arg_parser.parse_args()

        port = 21
        # Обрабатываем введеные параметры
        if args.host:
            host = args.host
        else:
            host = input('Enter host: ')
        if args.port:
            port = args.port
        self.client = ftp.FTPClient(host, port, active_mode=args.active,
                                    debug=args.debug)
        try:
            self.client.connect()
        except ftp.ConnectionErrorException:
            print('Connection error')
            exit(-1)

        if args.user:
            username = args.user
        else:
            username = input('Enter username: ')
        password = getpass.getpass('Enter password (or empty): ')

        try:
            self.client.login(username, password)
        except ftp.FTPException as e:
            print(e)
            exit(-1)

        while True:
            self.cmd_parse(input())

        self.client.disconnect()

    def cmd_parse(self, cmd_line):
        try:
            command, *arguments = cmd_line.split()
        except ValueError:
            return
        if command in self.handlers:
            self.handlers[command](arguments)
        else:
            print(helps.UNKNOWN_COMMAND)

    def help_handler(self, args):
        if len(args) == 0:
            print(helps.HELP_MSG)
        elif len(args) == 1:
            command = args[0]
            if command in self.helps:
                print(self.helps[command])
            else:
                print(helps.UNKNOWN_COMMAND)
        else:
            print('syntax error: try help help')

    def quit_handler(self, args):
        print('Bye!')
        exit()

    def cd_handler(self, args):
        if len(args) == 1:
            path_name = args[0]
            try:
                self.client.change_working_directory(path_name)
            except ftp.FTPException as e:
                print(e)
        else:
            print('syntax error: try help cd')

    def recursive_download(self, file_list):
        if not file_list:
            print('file list is empty')

        for file_name in file_list:
            try:
                data = self.client.retrieve(file_name)
                file = open(file_name, 'wb')
                file.write(data)
                file.close()
            except ftp.FTPException:
                os.mkdir(file_name)
                next_file_list = self.client.get_filename_list(file_name)
                if next_file_list:
                    self.recursive_download(next_file_list)

    def recv_handler(self, args):
        if len(args) >= 1:
            if args[0] == '-r':
                try:
                    self.recursive_download(args[1:])
                except ftp.FTPException as e:
                    print(e)
            else:
                for file_name in args:
                    try:
                        data = self.client.retrieve(file_name)
                        try:
                            file = open(file_name, 'wb')
                            file.write(data)
                            file.close()
                        except FileExistsError as e:
                            print(e)
                    except ftp.FTPException as e:
                        print(e)
        else:
            print('syntax error: try help recv')

    def recursive_upload(self, file_list):
        if not file_list:
            print('file list is empty')
        for file_name in file_list:
            if os.path.exists(file_name):
                if os.path.isdir(file_name):
                    basename = os.path.basename(file_name)
                    try:
                        self.client.make_directory(basename)
                    except ftp.FTPException:
                        pass
                    next_file_list = \
                        [file_name + '/' + x for x in os.listdir(file_name)]
                    if next_file_list:
                        self.client.change_working_directory(basename)
                        self.recursive_upload(next_file_list)
                        self.client.change_to_parent_directory()
                else:
                    file = open(file_name, 'rb')
                    data = file.read()
                    file.close()
                    self.client.store(
                        os.path.basename(file_name),
                        data
                    )
            else:
                print('File not exist: ' + file_name)

    def put_handler(self, args):
        if len(args) >= 1:
            if args[0] == '-r':
                try:
                    self.recursive_upload(args[1:])
                except ftp.FTPException as e:
                    print(e)
            else:
                for file_name in args:
                    if os.path.exists(file_name):
                        if os.path.isdir(file_name):
                            print('File is dir: ' + file_name)
                        else:
                            file = open(file_name, 'rb')
                            data = file.read()
                            file.close()
                            self.client.store(
                                os.path.basename(file_name),
                                data
                            )
        else:
            print('syntax error: try help recv')

    def ls_handler(self, args):
        if len(args) == 0:
            try:
                print(self.client.get_file_list())
            except ftp.FTPException as e:
                print(e)
        elif len(args) == 1:
            path_name = args[0]
            try:
                print(self.client.get_file_list(path_name))
            except ftp.FTPException as e:
                print(e)
        else:
            print('syntax error: try help ls')

    def cdup_handler(self, args):
        if len(args) == 0:
            try:
                self.client.change_to_parent_directory()
            except ftp.FTPException as e:
                print(e)
        else:
            print('syntax error: try help cdup')

    def mkdir_handler(self, args):
        if len(args) == 1:
            dir_name = args[0]
            try:
                self.client.make_directory(dir_name)
            except ftp.FTPException as e:
                print(e)
        else:
            print('syntax error: try help mkdir')


if __name__ == '__main__':
    ftp_cui = FtpCui()
    ftp_cui.run()
