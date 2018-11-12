# Copyright (C) 2018 Krishna Moniz

# This package contains the code for the CA
# This __init__ file will receive method calls from run.py (see parent directory)
# and forward them to the right module (see other py files in this folder)

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
from app.ca import CertAuthority
from app.openssl import create_pkcs12
from os import getenv, path
from flask import Flask, jsonify, url_for, send_from_directory, request
from werkzeug.utils import secure_filename

# -----------------------------------------------------------------------------------
# INITIALIZE FLASK APP
# -----------------------------------------------------------------------------------

# load the configuration
config = configparser.ConfigParser()
config.read(getenv('CONFIG_FILE'))
config_section = getenv('CONFIG_SECTION', 'ca')

# Initialize the Flask app
# TODO remove hardcoded upload folder
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/srv/www/certificate_authority/site/app/static'


# -----------------------------------------------------------------------------------
# HELPER METHODS
# -----------------------------------------------------------------------------------

def get_certificate_filename(fingerprint, key=False, p12=False):
    return secure_filename(fingerprint) + ('.p12' if p12 is True else '.key' if key is True else'.pem')


def create_cert(identity_id, passphrase, authorityID=None, Intermediate=False, p12=False):
    # TODO generate a certificate based on intermediate authority ID
    private_key, certificate = CertAuthority.createca('folder', 'passphrase')
    p12data = create_pkcs12(private_key, certificate)
    print('Created a certificate authority')

    # TODO get fingerprint
    fingerprint = 'this_is_a_fingerprint'

    # Save the result as p12 file
    # TODO separate into p12 and key/cert pair
    filename = get_certificate_filename(fingerprint, p12=True)
    with open(path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as p12file:
        p12file.write(p12data)

    return fingerprint


# -----------------------------------------------------------------------------------
# ROUTES
# -----------------------------------------------------------------------------------

@app.route('/verify', methods=['POST'])
def verify_certificate():
    """Verify the trust of a given certificate.
        JSON input (see reference below): {certificate}
        JSON output (see reference below): {valid}
        """

    # TODO send chain to certificate authority class with all valid root CA
    response = {'valid': True}
    return jsonify(response)


@app.route('/download/certificates/<string:fingerprint>')
def download_certificate(fingerprint):
    """Send a certificate file. Does not check for existence."""
    filename = get_certificate_filename(fingerprint)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/certificates/<string:identity_id>', methods=['GET'])
def post_certificates_id(identity_id):
    """Generate a certificate
        JSON output (see reference below): {ID, fingerprint, crypto, download}
       """

    # TODO get the identity that we're creating a certificate for
    print('DEBUG: Generate a certificate for an identity')
    name = {'cn': 'Krishna Moniz', 'o': 'K Organization', 'ou': 'Test department',
            'l': 'Paramaribo', 's': 'Paramaribo', 'c': 'SR', 'm': 'ca@krishna.sr'}
    identity = {'ID': identity_id, 'intermediate': False, 'fingerprint': None, 'download': None,
                'passphrase': 'passphrase', 'authorityID': '', 'name': name}

    # create a certificate
    passphrase = identity.get('passphrase')
    authorityID = identity.get('AuthorityID')
    fingerprint = create_cert(identity_id, passphrase, authorityID=authorityID, Intermediate=True, p12=True)

    response = {'ID': identity_id, 'fingerprint': fingerprint}
    response['download'] = url_for('download_certificate', fingerprint=fingerprint)

    # TODO update the old certificate
    # TODO figure out what to do with the old certificate (add to CRL / add copies)
    # TODO figure out response and failures
    return jsonify(response)


@app.route('/identities', methods=['GET'])
def get_identities():
    """Get a TLS identity.
        PARAM input (see reference below): authorityID & startID & count
        JSON output (see reference below): [{identity}, ...]
       """

    # TODO create a db entry that stores the identity
    # TODO figure out what to do with passphrase of intermediate certificates
    print('DEBUG: Request to create an identity')
    identity_id = request.args.get('authorityID')
    name = {'cn': 'Krishna Moniz', 'o': 'K Organization', 'ou': 'Test department',
            'l': 'Paramaribo', 's': 'Paramaribo', 'c': 'SR', 'm': 'ca@krishna.sr'}
    response = [{'ID': identity_id, 'intermediate': False, 'fingerprint': None, 'download': None, 'name': name}]

    # TODO figure out response and failures
    return jsonify(response)


@app.route('/identities/<string:identity_id>', methods=['GET'])
def get_identities_id(identity_id):
    """Get a TLS identity.
        JSON output (see reference below): {identity}
       """

    # TODO get a db entry from the certificate
    print('DEBUG: Request to get an identity')
    name = {'cn': 'Krishna Moniz', 'o': 'K Organization', 'ou': 'Test department',
            'l': 'Paramaribo', 's': 'Paramaribo', 'c': 'SR', 'm': 'ca@krishna.sr'}
    response = {'ID': identity_id, 'intermediate': False, 'fingerprint': None, 'download': None, 'name': name}

    # TODO figure out response and failures
    return jsonify(response)


@app.route('/identities', methods=['POST'])
def post_identities():
    """Create a TLS identity. This stores the identity information (common name, etc)
        and if requested generates a TLS certificate.
        JSON input (see reference below): {identity, generate}
        JSON output (see reference below): {identity, crypto}
        Ignored input: ID, fingerprint, download
    """

    # TODO create a db entry that stores the identity
    # TODO figure out what to do with passphrase of intermediate certificates
    print('DEBUG: Request to create an identity')
    params = request.get_json()
    identity_id = 1
    name = {'cn': 'Krishna Moniz', 'o': 'K Organization', 'ou': 'Test department',
            'l': 'Paramaribo', 's': 'Paramaribo', 'c': 'SR', 'm': 'ca@krishna.sr'}
    response = {'ID': identity_id, 'intermediate': False, 'fingerprint': None, 'download': None, 'name': name}

    if params.get('generate') is True:
        passphrase = params.get('passphrase')
        authorityID = params.get('AuthorityID')
        fingerprint = create_cert(identity_id, passphrase, authorityID=authorityID, Intermediate=True, p12=True)
        response['fingerprint'] = fingerprint
        response['download'] = url_for('download_certificate', fingerprint=fingerprint)

    # TODO determine what to do with crypto
    # TODO figure out response and failures
    return jsonify(response)


@app.route('/identities/<string:identity_id>', methods=['PUT'])
def put_identities_id(identity_id):
    """Update a TLS identity. This stores the identity information (common name, etc),
        resets the fingerprint to None and does not create TLS certificate.
        JSON input (see reference below): {identity}
        JSON output (see reference below): {identity}
        Ignored input: ID, fingerprint, download
    """

    # TODO update a db entry that stores the identity
    # TODO figure out what to do with passphrase and intermediate certificates
    # TODO figure out what to do with certificates
    print('DEBUG: Request to update an identity')
    name = {'cn': 'Krishna Moniz', 'o': 'K Organization', 'ou': 'Test department',
            'l': 'Paramaribo', 's': 'Paramaribo', 'c': 'SR', 'm': 'ca@krishna.sr'}
    response = {'ID': identity_id, 'intermediate': False, 'fingerprint': None, 'download': None, 'name': name}

    # TODO determine what to do with key and certificate
    # TODO figure out response and failures
    return jsonify(response)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    response = {'error':
                {'title': 'NOTFOUND',
                 'detail': 'CA resource not found',
                 'code': 404,
                 }
                }
    return jsonify(response), 404


# -----------------------------------------------------------------------------------
# JSON OBJECTS REFERENCE
# -----------------------------------------------------------------------------------
#
# RESOURCES
# - identity (json object):
#   - ID (str):             ID of the created identity
#   - authorityID (str):    ID the signing identity (None means self-signed / root)
#   - intermediate (bool):  True means the identity can act as an intermediate
#   - fingerprint (str):    None unless generate=True
#   - download (str):       Relative uri to download certificate (only if fingerprint!=None)
#   - passphrase (str):     Passphrase for the private key
#   - name (json object):
#     - cn (str): Common name of the identity,
#     - o (str):  Name of the organization,
#     - ou (str): Name of the organization unit/department,
#     - l (str):  Geographic Location/city of the identity,
#     - s (str):  State/district of the identity,
#     - c (str):  ISO 3166-1 alpha-2 country code of the identity,
#     - m (str):  e-Mail of the identity
#
# - crypto (json object):
#     - key (str):           String representation of the (encrypted) key
#     - certificate (str):   String representation of a PEM file
#
# - certificate (str):      String representation of a PEM file
# - valid (bool):           True if the given certificate is verified as valid
#
# COMMANDS
# - generate (bool): True will generate a certificate [default = False]
# - startID (str): start count from this ID [default=ID of the first record]
# - count (int): max number of identity records to return. Possible values: 10,20,50 [default=10]
# - authorityID (str): ID the signing identity
# -----------------------------------------------------------------------------------
