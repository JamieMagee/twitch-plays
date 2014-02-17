from lib.irc import Irc
from lib.game import Game
from lib.misc import pbutton

import time


class Bot:

    def __init__(self, config):
        self.config = config
        self.irc = Irc(config)
        self.game = Game()

    def run(self):
        last_start = time.time()

        while True:
            new_messages = self.irc.recv_messages(1024)
            
            if new_messages:
                for message in new_messages:
                    button = message['message'].lower()
                    username = message['username']

                    if not self.game.is_valid_button(button):
                        continue

                    if self.config['start_throttle']['enabled'] and button == 'start':
                        if time.time() - last_start < self.config['start_throttle']['time']:
                            continue

                    pbutton(username, button)
                    self.game.push_button(button)

                    if button == 'start':
                        last_start = time.time()

