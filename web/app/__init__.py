# Copyright (C) 2018 Krishna Moniz

# The routes for this flask app

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

import configparser
import redis
import time
import os
from flask import Flask, render_template, request

# load the configuration
config = configparser.ConfigParser()
config.read(os.getenv('CONFIG_FILE'))

# initialize the flask app and redis client
app = Flask(__name__)
redis_client = redis.StrictRedis(
    host=str(config['web']['redis_host']),
    port=int(config['web']['redis_port']))


@app.route('/')
@app.route('/index')
def index():

    # Get some data
    count = redis_client.incr('index_hits')
    right_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())

    # read the configuration
    redis_channel2 = str(config['web']['channel_in'])

    return """{}. WEB SERVICE ({}): config says {}.""".format(right_now, count, redis_channel2)


@app.route('/insert')
def other():

    # pull some variables from the config
    count = redis_client.incr('insert_hits')
    ca_channel_in = str(config['ca']['channel_in'])

    # publish the message
    param = '!!!ERROR: PLEASE PROVIDE A QUERY PARAM!!!'
    if request.args.get('a') is not None:
        param = str(request.args.get('a'))
        timeout_start = time.time()
        timeout = 5
        while time.time() < timeout_start + timeout:
            try:
                rcvd = redis_client.publish(ca_channel_in, param)
                if rcvd > 0:
                    redis_client.set('param', param, ex=30)
                    break
            except redis.ConnectionError:
                print('Error: No one is subscribed to {}.'.format(ca_channel_in))

    return """PUBLISH ATTEMPT ({}): {} >> {}.""".format(count, ca_channel_in, param)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404