import ftp
import os

help_msg = """exit
(dir|ls) [<path_name>]
recv <file_name>
cd <path_name>
put <file_path>"""

# 'shannon.usu.edu.ru'

if __name__ == '__main__':
    # host = input('Enter host: ')
    host = 'kottsarapkin.16mb.com'
    client = ftp.FTPClient(host, debug=True)
    # login = input('Enter login: ')
    login = 'u255347692'
    # password = input('Enter password: ')
    password = 'c10n4td1'
    client.connect()
    client.login(login, password)

    while True:
        cmd = input()
        if cmd == 'exit':
            print('Bye!')
            break
        elif cmd.startswith('dir ') or cmd.startswith('ls '):
            try:
                path_name = cmd.split()[1]
            except IndexError:
                print('syntax error: dir [<path_name>]')
                continue
            try:
                print(client.get_file_list(path_name))
            except ftp.FTPException as e:
                print(e)
        elif cmd in ('dir', 'ls'):
            try:
                print(client.get_file_list())
            except ftp.FTPException as e:
                print(e)
        elif cmd.startswith('recv '):
            try:
                file_name = cmd.split()[1]
            except IndexError:
                print('syntax error: recv <file_name>')
                continue
            try:
                client.retrieve(file_name)
            except ftp.FTPException as e:
                print(e)
        elif cmd.startswith('cd '):
            try:
                path_name = cmd.split()[1]
            except IndexError:
                print('syntax error: cd <path_name>')
                continue
            client.change_working_directory(path_name)
        elif cmd == 'cdup':
            try:
                client.change_to_parent_directory()
            except ftp.FTPException as e:
                print(e)
        elif cmd.startswith('put '):
            try:
                file_path = cmd.split()[1]
            except IndexError:
                print('syntax error: put <file_path>')
                continue
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    data = file.read()
                file_name = os.path.basename(file_path)
                print(file_name)
                try:
                    client.store(file_name, data)
                except ftp.FTPException as e:
                    print(e)
            else:
                print('File {} not exist'.format(file_path))
        elif cmd == 'help':
            print(help_msg)
        else:
            print('error: unknown command')

    client.disconnect()