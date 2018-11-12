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

import time
import requests


def add(x, y, auth_id=None):
    print('sync: start')
    time.sleep(2)
    print('sync: end')
    return x + y


# -----------------------------------------------------------------------------------
# DIENST tasks
# -----------------------------------------------------------------------------------

def get_data(self, data_id=None, count=0):
    """Forward the request to DIENST. No data validity checks are made!!!"""

    self.update_state(state='STARTED')
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
