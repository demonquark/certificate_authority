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
import requests
import time
from os import getenv
from celery import Celery
from flask import Flask, render_template, jsonify, url_for, request
from internal_api import async_api, sync_api

# -----------------------------------------------------------------------------------
# INITIALIZE FLASK APP
# -----------------------------------------------------------------------------------

# load the configuration
config = configparser.ConfigParser()
config.read(getenv('CONFIG_FILE'))
config_section = getenv('CONFIG_SECTION', 'web')

# Initialize the Flask app
app = Flask(__name__)

# Initialize redis
redis_client = redis.StrictRedis(
    host=str(config[config_section]['redis_host']),
    port=int(config[config_section]['redis_port']))

# Initialize celery
celery = Celery(
    str(config[config_section]['celery_name']),
    broker=str(config[config_section]['celery_broker_url']),
    backend=str(config[config_section]['celery_result_backend']))
celery.conf.result_expires = int(config[config_section]['celery_task_result_expires'])


# -----------------------------------------------------------------------------------
# HELPER METHODS
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
# ROUTES
# -----------------------------------------------------------------------------------

@app.route('/')
@app.route('/index')
def index():
    # Get some data
    count = redis_client.incr('index_hits')
    right_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    the_keys = redis_client.keys()

    # return something
    return """<html><body>API SERVICE ({}): {} <br />{}</body></html>""".format(count, right_now, the_keys)


@app.route('/data', methods=['GET'])
def get_data():
    """Get data records.
        PARAM input (see reference below): startID & count
        output: status redirect
       """

    # TODO get a db entry from data
    print('DEBUG: Request to get data')
    data_id = request.args.get('startID')
    count = request.args.get('count')

    auth_id = str(request.headers.get('Authorization'))
    task = async_api.get_data(data_id=data_id, count=count)
    print('data: [' + auth_id + '] ' + str(task))

    # TODO figure out response and failures
    return jsonify({}), 303, {'Location': url_for('status_data', task_id=task.id)}


@app.route('/data/<string:data_id>', methods=['GET'])
def get_data_id(data_id):
    """Get a data record.
        JSON output (see reference below): {data}
       """

    # TODO get a db entry from data
    print('DEBUG: Request to get data')
    response = sync_api.get_data(data_id=data_id)

    # TODO figure out response and failures
    return jsonify(response)


@app.route('/status/data/<string:task_id>', methods=['GET'])
def status_data(task_id):
    """Get the status of data request.
        JSON output (see reference below): {status}
       """

    # default values
    response = {}
    response_code = 200
    response_detail = 'The requested task does not exist.'

    # get the task status
    auth_id = str(request.headers.get('Authorization'))
    auth_ex = str(None)
    task = celery.AsyncResult(task_id)

    # parse the task status
    if task is None or str(task.state) == 'FAILURE' or str(task.state) == 'REVOKED':
        response_code = 400
        response_detail = 'Failed to report task status.'
    elif str(task.state) == 'PENDING':
        response_code = 202
        response_detail = 'Task is pending.'
    elif task.info is not None:
        # elif task.info is not None and str(task.info.get('auth_id')) is auth_id:
        # auth_ex = str(task.info.get('auth_id'))
        response_code = 200 if str(task.state) == 'SUCCESS' else 202
        # response_detail = task.info.get('data')
        response_detail = 'The task is either done or status'
    else:
        response_code = 403
        response_detail = 'You are not authorized to access this resource.'

    # build a response
    if response_code == 200:
        print('---------------')
        print(task.info)
        print('----------------')
    elif response_code < 400:
        response = {'data':
                    {'type': 'status',
                     'id': str(task_id),
                     'attributes':
                     {'title': str(task.state),
                      'detail': response_detail,
                      'auth_id': auth_id,
                      'auth_ex': auth_ex
                      }
                     }
                    }
    else:
        response = {'error':
                    {'title': 'NOTFOUND' if task is None else str(task_id),
                     'detail': response_detail,
                     'auth_id': auth_id,
                     'code': response_code,
                     }
                    }

    print(str(response_code) + ' [' + auth_id + ']: ' + str(redis_client.get('celery-task-meta-' + str(task_id))))
    return jsonify(response), response_code, {'Location': url_for('status_data', task_id=task_id)}


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    response = {'error':
                {'title': 'NOTFOUND',
                 'detail': 'API resource not found',
                 'code': 404,
                 }
                }
    return jsonify(response), 404
