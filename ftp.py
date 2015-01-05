__author__ = 'Kovrizhnykh Alexey'

import socket
import re
import threading


class FTPException(Exception):
    pass


class ConnectionErrorException(FTPException):

    def __init__(self, msg):
        super().__init__(msg)


class UnexpectedReplyException(FTPException):

    def __init__(self, command, reply):
        msg = '{}: unexpected reply:\n{}\n'.format(command, reply)
        super().__init__(msg)


class ErrorException(FTPException):

    def __init__(self, command, msg):
        msg = '{} error:\n{}\n'.format(command, msg)
        super().__init__(msg)


class FailureException(FTPException):

    def __init__(self, command, msg):
        msg = '{} failure:\n{}\n'.format(command, msg)
        super().__init__(msg)


class FTPClient:
    """
    FTP-клиент
    """

    BUFFER_SIZE = 2 ** 16
    # Регвыр для извлечения адреса из сообщения
    addr_regexp = re.compile(r'\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)')
    ACTIVE_PORT = 60666

    def __init__(self, host, port=21, active_mode=False, debug=False):
        # Адрес сервера
        self.host = host
        # Порт сервера
        self.port = port
        # Флаг отладочного режима
        self.debug = debug
        # Управляющий соккет
        self.control_socket = socket.socket()
        self.control_socket.settimeout(10.0)
        # Флаг пасссивного режима
        self.passive_mode = not active_mode
        self.data_transfer_socket = None

    def send_command(self, command):
        if self.debug:
            print('---> ' + command)
        self.control_socket.send((command + '\r\n').encode())

    def get_line(self):
        """
        Считать строку с управляющего сркета
        """
        line = b''
        while True:
            byte = self.control_socket.recv(1)
            if byte == b'\n' or byte == b'':
                if self.debug:
                    print('<--- ' + line.decode())
                return line.decode()
            else:
                line += byte

    def get_reply(self):
        """
        Получить ответ с сервера
        """
        reply_lines = []
        while True:
            line = self.get_line()
            reply_lines.append(line)
            if line[3] != '-':
                return int(line[:3]), '\n'.join(reply_lines)

    def connect(self):
        """
        Соединиться с сервером
        """
        try:
            self.control_socket.connect((self.host, self.port))
            while True:
                code, reply = self.get_reply()
                code_type = code // 100
                if code_type == 4:
                    raise ConnectionErrorException(reply)
                elif code_type == 2:
                    return
                else:
                    raise UnexpectedReplyException(reply)
        except socket.error:
            raise ConnectionErrorException('')

    def login(self, login, password):
        """
        Вход
        """
        self.send_command('USER ' + login)
        while True:
            code, reply = self.get_reply()
            code_type = code // 100
            if code_type == 1:
                raise ErrorException(
                    'USER', reply
                )
            elif code_type == 2:
                return
            elif code_type in (4, 5):
                raise FailureException(
                    'USER', reply
                )
            elif code_type == 3:
                break
        self.send_command('PASS ' + password)
        while True:
            code, reply = self.get_reply()
            code_type = code // 100
            if code_type == 1:
                raise ErrorException(
                    'PASS', reply
                )
            elif code_type == 2:
                return
            elif code_type in (4, 5):
                raise FailureException(
                    'PASS', reply
                )
            elif code_type == 3:
                break
        raise FTPException('ACCT not supported')

    def disconnect(self):
        """
        Отключиться от сервера
        """
        if self.debug:
            print('---> Disconnecting...')
        self.control_socket.close()

    def send_command_std_model(self, command, expects_100=False):
        """Обрабатывает команды по станартной модели.
        В RFC-959 описаны две большие группы команд, обрабатываемые
        по определенной модели.
        """
        self.send_command(command)
        while True:
            code, reply = self.get_reply()
            code_type = code // 100
            if code_type == 1 and expects_100:
                continue
            elif code_type in (1, 3):
                raise ErrorException(
                    command, reply
                )
            elif code_type == 2:
                return reply
            elif code_type in (4, 5):
                raise FailureException(
                    command, reply
                )
            else:
                raise UnexpectedReplyException(
                    command, reply
                )

    def init_data_transfer_socket(self):
        self.data_transfer_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.data_transfer_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )
        self.data_transfer_socket.settimeout(5)
        if self.passive_mode:
            reply = self.send_command_std_model('PASV')
            match = self.addr_regexp.search(reply)
            numbers = match.groups()
            dt_addr = '.'.join(numbers[:4])
            dt_port = int(numbers[4]) << 8 | int(numbers[5])
            self.data_transfer_socket.connect((dt_addr, dt_port))
        else:
            self.data_transfer_socket.bind(('', self.ACTIVE_PORT))
            self.data_transfer_socket.listen(100)
            self.send_command_std_model('PORT 127,0,0,1,{},{}'.format(
                (self.ACTIVE_PORT & 0xff00) >> 8, self.ACTIVE_PORT & 0x00ff
            ))

    def recv_from_data_transfer_socket(self):
        data = None
        if self.passive_mode:
            data = self.data_transfer_socket.recv(self.BUFFER_SIZE)
            self.data_transfer_socket.close()
        else:
            server_connection, (addr, port) = \
                self.data_transfer_socket.accept()
            data = server_connection.recv(self.BUFFER_SIZE)
            server_connection.close()
            self.data_transfer_socket.close()
        return data

    def send_to_data_transfer_socket(self, data):
        if self.passive_mode:
            self.data_transfer_socket.send(data)
            self.data_transfer_socket.close()
        else:
            def sending_thread(sock):
                server_connection, (addr, port) = \
                    self.data_transfer_socket.accept()
                server_connection.send(data)
                server_connection.close()
                sock.close()
            threading.Thread(
                target=sending_thread,
                args=(self.data_transfer_socket,)
            ).start()

    def get_file_list(self, pathname=''):
        self.init_data_transfer_socket()
        command = 'LIST'
        if pathname:
            command += ' ' + pathname
        self.send_command_std_model(command, expects_100=True)
        file_list = self.recv_from_data_transfer_socket()
        return file_list.decode()

    def get_filename_list(self, pathname=''):
        self.init_data_transfer_socket()
        command = 'NLST'
        if pathname:
            command += ' ' + pathname
        self.send_command_std_model(command, expects_100=True)
        filename_list = self.recv_from_data_transfer_socket().decode().split()
        return filename_list

    def change_to_parent_directory(self):
        self.send_command_std_model('CDUP')

    def change_working_directory(self, pathname):
        self.send_command_std_model('CWD ' + pathname)

    def make_directory(self, pathname):
        self.send_command_std_model('MKD ' + pathname)

    def retrieve(self, file_name):
        """
        Скачать файл
        """
        self.init_data_transfer_socket()
        self.send_command_std_model('RETR ' + file_name, expects_100=True)
        return self.recv_from_data_transfer_socket()

    def store(self, file_name, data):
        """
        Загрузить файл
        """
        self.init_data_transfer_socket()
        self.send_to_data_transfer_socket(data)
        self.send_command_std_model('STOR ' + file_name, expects_100=True)
