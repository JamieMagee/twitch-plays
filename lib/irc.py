import socket
import sys
import re
from lib.misc import *


class Irc:
    def __init__(self, config):
        self.config = config
        self.set_socket_object()

    def set_socket_object(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = sock

        sock.settimeout(10)

        username = self.config['account']['username']
        password = self.config['account']['password']

        server = self.config['irc']['server']
        port = self.config['irc']['port']

        try:
            sock.connect((server, port))
        except:
            pp('Error connecting to server.', 'error')
            self.set_socket_object()

        sock.settimeout(None)

        sock.send('USER {}\r\n'.format(username).encode('UTF-8'))
        sock.send('PASS {}\r\n'.format(password).encode('UTF-8'))
        sock.send('NICK {}\r\n'.format(username).encode('UTF-8'))

        if not self.check_login_status(self.recv()):
            pp('Invalid login.', 'error')
            sys.exit()
        else:
            pp('Login successful!')

        sock.send('JOIN #{}\r\n'.format('twitchplayspokemon').encode('UTF-8'))
        pp('Joined #%s\n\n' % 'twitchplayspokemon')

    def ping(self, data):
        if data.startswith('PING'.encode('UTF-8')):
            self.sock.send(data.replace('PING'.encode('UTF-8'), 'PONG'.encode('UTF-8')))

    def recv(self, amount=1024):
        return self.sock.recv(amount)

    def recv_messages(self, amount=1024):
        data = self.recv(amount)

        if not data:
            pbot('Lost connection, reconnecting.')
            self.set_socket_object()
            return self.recv_messages(amount)

        self.ping(data)

        if self.check_has_message(data):
            data = filter(None, data.decode().split('\r\n'))
            return [self.parse_data_for_message(line) for line in data]

    @staticmethod
    def check_login_status(data):
        if not re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data.decode()):
            return True

    @staticmethod
    def check_has_message(data):
        return re.match(
            r'^:[a-zA-Z0-9_]+![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$',
            data.decode('UTF-8'))

    @staticmethod
    def parse_data_for_message(data):
        channel = re.findall(r'^:.+![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0]
        username = re.findall(r'^:([a-zA-Z0-9_]+)!', data)[0]
        message = re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0]

        return {
            'channel': channel,
            'username': username,
            'message': message
        }

