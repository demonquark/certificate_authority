# Copyright (C) 2018 Krishna Moniz

# A python implementation of the other docker containers api calls
# Use the tasks defined in this module in your flask / django app
# to communicate with other microservices in the docker network

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
import time
import requests
from os import getenv
from celery import Celery


# load the configuration
config = configparser.ConfigParser()
config.read(getenv('CONFIG_FILE'))
config_section = getenv('CONFIG_SECTION', 'web')

# Initialize celery
celery = Celery(
    str(config[config_section]['celery_name']),
    broker=str(config[config_section]['celery_broker_url']),
    backend=str(config[config_section]['celery_result_backend']))
celery.conf.result_expires = int(config[config_section]['celery_task_result_expires'])


@celery.task(bind=True, track_started=True)
def add(self, x, y, auth_id=None):

    self.update_state(state='STARTED', meta={'data': 'start', "auth_id": str(auth_id)})
    print('async: start it')
    time.sleep(2)
    print('async: phase 1')
    self.update_state(state='STARTED', meta={'data': x, "auth_id": str(auth_id)})
    time.sleep(2)
    print('async: phase 2')
    self.update_state(state='STARTED', meta={'data': y, "auth_id": str(auth_id)})
    time.sleep(2)
    print('async: phase 3')
    self.update_state(state='STARTED', meta={'data': (x + y), "auth_id": str(auth_id)})
    time.sleep(2)
    print('async: end it')
    return {"data": (str(x) + ' + ' + str(y) + ' = ' + str(x + y)), "auth_id": str(auth_id)}


@celery.task(bind=True, track_started=True)
def createca(self, auth_id=None):

    print('createca task: ' + str(self.request.id))
    url = 'http://ca:8000/createca/' + str(self.request.id)
    data = requests.get(url=url)

    try:
        print('Celery result1: ' + str(data))
        json_data = data.json()
        print('Celery result2: ' + str(json_data))
    except Exception as e:
        print('Celery result3: ' + str(e))

    return {"data": json_data, "inside_id": str(self.request.id), "auth_id": str(auth_id)}


# -----------------------------------------------------------------------------------
# CA tasks
# -----------------------------------------------------------------------------------

@celery.task(bind=True, track_started=True)
def verify_certificate(self, certificate):
    """Forward the request to the CA. No data validity checks are made!!!"""

    # self.update_state(state='STARTED')
    print('verify task: ' + str(self.request.id))

    # send the request
    url = 'http://ca:8000/verify/'
    data = requests.post(url=url, data={'certificate': certificate})

    return data


# -----------------------------------------------------------------------------------
# DIENST tasks
# -----------------------------------------------------------------------------------

@celery.task(bind=True, track_started=True)
def get_data(self, data_id=None, count=0):
    """Forward the request to DIENST. No data validity checks are made!!!"""

    # self.update_state(state='STARTED')
    print('get signature task: ' + str(self.request.id))

    # send the request
    if count is not None and count > 1:
        params = {'startID': data_id, 'count': count}
        url = 'http://dienst:8000/data/' + str(data_id)
        data = requests.get(url=url, params=params)
    else:
        url = 'http://dienst:8000/data/'
        data = requests.get(url=url)

    # try:
    #     print('Celery result1: ' + str(data))
    #     json_data = data.json()
    #     print('Celery result2: ' + str(json_data))
    # except Exception as e:
    #     print('Celery result3: ' + str(e))

    return data
