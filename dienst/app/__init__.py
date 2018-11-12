# Copyright (C) 2018 Krishna Moniz

# This package contains the code for the data service
# The package contains users and data. Users can sign data with a digital signature.
# This __init__ file will receive method calls from run.py (see parent directory)
# and forward them to the right module (see other py files in this folder)

# Endpoints:
# /download/signatures/<string:filename>
# /signatures/<string:file_type>/<string:data_id>
# /users
# /users/<string:user_id>
# /data
# /data/<string:data_id>

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
from os import getenv, path
from flask import Flask, jsonify, url_for, send_from_directory, request
from werkzeug.utils import secure_filename

# -----------------------------------------------------------------------------------
# INITIALIZE FLASK APP
# -----------------------------------------------------------------------------------

# load the configuration
config = configparser.ConfigParser()
config.read(getenv('CONFIG_FILE'))
config_section = getenv('CONFIG_SECTION', 'dienst')

# Initialize the Flask app
# TODO remove hardcoded upload folder
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/srv/www/certificate_authority/site/app/static'


# -----------------------------------------------------------------------------------
# HELPER METHODS
# -----------------------------------------------------------------------------------

def get_signature_filename(data_id, pdf=False):
    return secure_filename(data_id) + ('.pdf' if pdf is True else '.jpg')


def create_signature_file(data, pdf=False):
    # TODO create logic to write data to a pdf file
    print('Convert signature data to file')
    file_content = 'base64 string of data??'

    # Save the result as a pdf file
    # TODO separate logic of base64 and pdf and jpg
    filename = get_signature_filename(data.get('ID'), pdf=True)
    with open(path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as signature_file:
        signature_file.write(file_content)

    return file_content, filename


def sign(payload, private_key):
    # TODO implement signing method
    return 'signed text'


def generate_identity(user):
    # TODO contact CA and get an identity
    response_from_ca = {'identity': {'ID': 1}, 'crypto': {'key': 'private_key', 'certificate': 'certificate'}}
    identity = response_from_ca.get('identity')
    return identity.get('ID'), response_from_ca.get('crypto')


def read_user(user_id):
    # TODO get the certificate from the data (should I store certificates in the DB or on file??? suggest: DB)
    # TODO replace this dict with a class
    user = {'private_key': 'a private key', 'certificate': 'PEM certificate of the user'}
    return user


def read_data(data_id):
    # TODO filter out data elements??? (no... That's web api logic)
    # TODO replace this dict with a class
    data_id = 1
    payload = {'title': 'foo', 'detail': 'bar', 'expiration': '20190101'}
    data = {'ID': data_id, 'payload': payload, 'signatory': None, 'signature': None}
    return data


def write_user(user_id):
    # TODO get the certificate from the data (should I store certificates in the DB or on file??? suggest: DB)
    # TODO replace this dict with a class
    user = {'private_key': 'a private key', 'certificate': 'PEM certificate of the user'}
    return user


def write_data(payload, user_id):
    # TODO create a db entry that stores the data
    # TODO figure out how best to handle signatures
    data_id = 1
    payload = {'title': 'foo', 'detail': 'bar', 'expiration': '20190101'}
    data = {'ID': data_id, 'payload': payload, 'signatory': None, 'signature': None}

    # sign the data if possible
    user = read_user(user_id)
    if user.get('private_key') is not None:
        signatory = user.get('certificate')
        signature = sign(payload, user.get('private_key'))
        data['signatory'] = signatory
        data['signature'] = signature

    return data


# -----------------------------------------------------------------------------------
# ROUTES
# -----------------------------------------------------------------------------------

@app.route('/download/signatures/<string:filename>')
def download_signature(filename):
    """Send a signature file. Does not check for existence."""
    secure_filename = get_signature_filename(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename, as_attachment=True)


@app.route('/signatures/<string:file_type>/<string:data_id>', methods=['GET', 'POST'])
def post_signatures_id(file_type, data_id):
    """Generate a signature file of the data
        JSON output (see reference below): {download}
       """

    print('DEBUG: Generate a file for this data')
    # TODO check the possible file names
    if file_type == 'pdf':
        # TODO get the data that we're creating a file for
        data_id = 1
        payload = {'title': 'foo', 'detail': 'bar', 'expiration': '20190101'}
        data = {'ID': data_id, 'payload': payload, 'signatory': None, 'signature': None}

        # create a file
        # TODO split base64 logic from file creation logic???
        file_content, filename = create_signature_file(data, pdf=True)
        if request.method == 'GET':
            response = {'file': file_content}
        else:
            response = {'download': url_for('download_signature', filename=filename)}
    else:
        response = {'error': {'title': 'INVALID INPUT',
                              'detail': 'File type should be pdf',
                              'code': 400}}

    # TODO figure out response and failures
    return jsonify(response)


@app.route('/users', methods=['GET'])
def get_users():
    """Get users.
        PARAM input (see reference below): startID & count
        JSON output (see reference below): [{user}, ...]
       """

    # TODO get a db entry from the user
    print('DEBUG: Request to get users')
    user_id = request.args.get('startID')

    response = [read_user(user_id)]

    # TODO figure out response and failures
    return jsonify(response)


@app.route('/users/<string:user_id>', methods=['GET'])
def get_user_id(user_id):
    """Get a user.
        JSON output (see reference below): {identity}
       """

    # TODO get a db entry from the user
    print('DEBUG: Request to get a user')
    response = read_user(user_id)

    # TODO figure out response and failures
    return jsonify(response)


@app.route('/data', methods=['GET'])
def get_data():
    """Get data records.
        PARAM input (see reference below): startID & count
        JSON output (see reference below): [{data}, ...]
       """

    # TODO get a db entry from data
    print('DEBUG: Request to get users')
    data_id = request.args.get('startID')

    response = [read_data(data_id)]

    # TODO figure out response and failures
    return jsonify(response)


@app.route('/data/<string:data_id>', methods=['GET'])
def get_data_id(data_id):
    """Get a TLS identity.
        JSON output (see reference below): {identity}
       """

    # TODO get a db entry from data
    print('DEBUG: Request to get a user')
    response = read_data(data_id)

    # TODO figure out response and failures
    return jsonify(response)


@app.route('/users', methods=['POST'])
@app.route('/users/<string:user_id>', methods=['POST'])
def post_users(user_id=None):
    """Create a user.
        JSON input (see reference below): {user}
        JSON output (see reference below): {user}
        Ignored input: ID, identity, crypto
    """

    # TODO remove ID, identity and crypto ???
    print('DEBUG: Request to create a user')
    params = request.get_json()

    # TODO contact the CA and generate an identity
    user = params.get('user')
    identity, crypto = generate_identity(user)
    user['identity'] = identity
    user['crypto'] = crypto

    # TODO write the user to db
    response = write_user(user)

    # TODO figure out response and failures
    return jsonify(response)


@app.route('/data', methods=['POST'])
def post_data():
    """Create data. If a known user_id is provided, the system will also sign the data.
        JSON input (see reference below): {data, user_id}
        JSON output (see reference below): {data}
        Ignored input: ID, signatory, signature
    """

    print('DEBUG: Request to create data')
    params = request.get_json()
    response = write_data(params.get('payload'), params.get('user_id'))

    # TODO figure out response and failures
    return jsonify(response)


@app.route('/data/<string:data_id>', methods=['PUT'])
def put_data_id(data_id):
    """Update data. This provided payload in as data.
        If a known user_id is provided, the system will also sign the data.
        JSON input (see reference below): {data, user_id}
        JSON output (see reference below): {data}
        Ignored input: ID, signatory, signature
    """

    # TODO test if the data already exists, only update??
    print('DEBUG: Request to update data')
    params = request.get_json()
    response = write_data(params.get('payload'), params.get('user_id'))

    # TODO figure out response and failures
    return jsonify(response)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    response = {'error':
                {'title': 'NOTFOUND',
                 'detail': 'Dienst resource not found',
                 'code': 404,
                 }
                }
    return jsonify(response), 404


# -----------------------------------------------------------------------------------
# JSON OBJECTS REFERENCE
# -----------------------------------------------------------------------------------
#
# RESOURCES
# - user (json object):
#   - ID (str):             ID of the user
#   - identity (str):       ID of the CA identity
#   - passphrase (str):     Passphrase for the private key
#   - crypto (json object):
#     - key (str):            Private key
#     - certificate (str):    TLS certificate
#   - name (json object):
#     - cn (str): Common name of the identity,
#     - o (str):  Name of the organization,
#     - ou (str): Name of the organization unit/department,
#     - l (str):  Geographic Location/city of the identity,
#     - s (str):  State/district of the identity,
#     - c (str):  ISO 3166-1 alpha-2 country code of the identity,
#     - m (str):  e-Mail of the identity
#
# - data (json object):
#   - ID (str):              ID of the data
#   - payload (json object): The payload is the actual data.
#       - title (str):          Some text
#       - detail (str):         Some more text
#       - value (int):          And an integer
#       - expiration (str):     An expiration date for the payload
#   - signatory (str):       TLS certificate of signatory (None if payload is not signed)
#   - signature (str):       Digital signature of the payload
#
# - download (str):       Relative uri to download signature file
# - file (str):           Base64 string representation of the signature file
#
# COMMANDS
# - user_id (str): The ID of the signatory. The data will be signed with this user's key
# - startID (str): start count from this ID [default=ID of the first record]
# - count (int): max number of data/user records to return. Possible values: 10,20,50 [default=10]
# - authorityID (str): ID the signing identity
# -----------------------------------------------------------------------------------
