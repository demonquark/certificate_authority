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


@app.route('/')
@app.route('/index')
def index():
    # Get some data
    count = redis_client.incr('index_hits')
    right_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    the_keys = redis_client.keys()

    # Print the keys
    for key in the_keys:
        if key.decode('utf-8') == 'celery-task-meta-13d7339c-0785-49dc-b3ee-74828524c773':
            print(redis_client.get(key))

    # return something
    return """<html><body>WEB SERVICE ({}): {} <br />{}</body></html>""".format(count, right_now, the_keys)


@app.route('/task')
def taskpage():
    # Return the task template
    return render_template('index.html'), 200


@app.route('/sync', methods=['POST'])
def run_sync_task():
    # Get some data
    result = sync_api.add(1, 2)
    print('synctask: ' + str(result))
    time.sleep(2)
    response = {'data':
                {'type': 'status',
                 'id': 'xxxx',
                 'attributes':
                 {'title': 'SUCCESS',
                  'detail': 'detailtext',
                  'auth_id': 'a70847a5-333d-3abf-b316-ec2b67bb8af8',
                  'auth_ex': 'a70847a5-333d-3abf-b316-ec2b67bb8af8'
                  }
                 }
                }

    return jsonify(response), 200, {'Location': url_for('run_sync_task')}


@app.route('/dotask', methods=['POST'])
def run_task():
    # Forward the task
    auth_id = str(request.headers.get('Authorization'))
    task = async_api.createca.delay(auth_id=auth_id)
    print('dotask: [' + auth_id + '] ' + str(task))

    return jsonify({}), 303, {'Location': url_for('taskstatus', task_id=task.id)}


@app.route('/download', methods=['GET'])
def download_file():
    # Forward the task
    url = "http://ca:8000/static/bestand.mp3"
    resp = requests.get(url, stream=True)
    resp.headers['Location'] = url_for('download_file')

    return resp.raw.read(), resp.status_code, resp.headers.items()


@app.route('/status/<task_id>', methods=['GET'])
def taskstatus(task_id):
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
    elif task.info is not None and str(task.info.get('auth_id')) == auth_id:
        # elif task.info is not None and str(task.info.get('auth_id')) is auth_id:
        auth_ex = str(task.info.get('auth_id'))
        response_code = 200 if str(task.state) == 'SUCCESS' else 202
        response_detail = task.info.get('data')
    else:
        response_code = 403
        response_detail = 'You are not authorized to access this resource.'

    # build a response
    if response_code == 200:
        print('---------------2')
        print(task.info.get('data'))
        print(task.info.get('data').get('download'))
        download_url = 'http://ca:8000' + str(task.info.get('data').get('download'))
        print(download_url)
        print('----------------')

        data = task.info.get('data')
        if data is not None and data.get('error') is not None:
            error = data.get('error')
            response_code = error.get('code') if error.get('code') is not None else 400
        else:
            resp = requests.get(download_url, stream=True)
            resp.headers['Location'] = url_for('taskstatus', task_id=task_id)
            return resp.raw.read(), resp.status_code, resp.headers.items()
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

    # right_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    print(str(response_code) + '| status: [' + auth_id + '] ' + str(redis_client.get('celery-task-meta-' + str(task_id))))
    return jsonify(response), response_code, {'Location': url_for('taskstatus', task_id=task_id)}


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404
