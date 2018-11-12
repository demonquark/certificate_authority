"""
This module contains the Certificate Authority class that handles PKI related functionality.
Copyright (C) 2018 Krishna Moniz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
# from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from OpenSSL import crypto


def create_pkcs12(private_key: rsa.RSAPrivateKeyWithSerialization,
                  certificate: x509.Certificate,
                  passphrase: str=None):
    """Create a PKCS#12 container from the given RSA key and Certificate"""
    p12 = crypto.PKCS12()
    pkey = crypto.PKey.from_cryptography_key(private_key)
    p12.set_privatekey(pkey)
    cert = crypto.X509.from_cryptography(certificate)
    p12.set_certificate(cert)

    return p12.export(str(passphrase))
