# Copyright (C) 2018 Krishna Moniz

# Message subscriber logic. Receives a message from redis
# and forwards it to the corresponding package method

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import signal
import configparser
import redis
import time
import os
from app import perform_action


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


if __name__ == "__main__":

    # graceful killer
    killer = GracefulKiller()

    # read the configuration
    config = configparser.ConfigParser()
    config.read(os.getenv('CONFIG_FILE'))
    redis_host = str(config['ca']['redis_host'])
    redis_port = int(config['ca']['redis_port'])
    redis_channel = str(config['ca']['channel_in'])

    # start a redis consumer
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port)
    p = redis_client.pubsub()
    p.subscribe(redis_channel)
    while True:
        try:
            message = p.get_message()
        except redis.ConnectionError as e:
            # Something went wrong with redis. Try reconnecting.
            print('ERROR')
            p = redis_client.pubsub()
            p.subscribe(redis_channel)
        if message:
            # do something with the message
            perform_action(message)
        # wait some time before querying for a new message
        if killer.kill_now:
            break
        time.sleep(0.5)
