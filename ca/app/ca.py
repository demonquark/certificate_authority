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
import os
import sys
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography import x509


class CertAuthority(object):
    """represents a CA"""
    def __init__(self, path, passphrase=None, load_files=True):
        """Initializes the CA"""
        # initialize CA variables
        self.path = str(path)
        self.algorithm = None
        self.private_key = None
        self.certificate = None

        # convert the passphrase to bytes
        if passphrase is not None:
            passphrase = str(passphrase).encode()

        # by default load the certificate and key
        if bool(load_files):
            # read the CA key
            filename_key = os.path.join(self.path, 'key.priv')
            if os.path.exists(filename_key):
                with open(filename_key, 'rb') as pem_in:
                    key_in = pem_in.read()
                self.private_key = serialization.load_pem_private_key(key_in, passphrase, default_backend())

            # read the CA certificate
            filename_crt = os.path.join(self.path, 'cert.pem')
            if os.path.exists(filename_crt):
                with open(filename_crt, 'rb') as pem_in:
                    crt_in = pem_in.read()
                self.certificate = x509.load_pem_x509_certificate(crt_in, default_backend())

            # determine the algorithm
            if isinstance(self.private_key, rsa.RSAPrivateKey):
                self.algorithm = 'RSA'
            elif isinstance(self.private_key, ec.EllipticCurvePrivateKey):
                self.algorithm = 'ECDSA'
            else:
                raise TypeError('The provided path does not contain a RSA or ECDSA key')

            # determine if this is a CA
            constraints = self.certificate.extensions.get_extension_for_oid(x509.oid.ExtensionOID.BASIC_CONSTRAINTS)
            if constraints.value.ca is not True:
                raise TypeError('The provided certificate cannot be a CA')

    def createname(self, cn: str='Krishna Intermediate CA', o: str='Krishna Organization', ou: str='Test Department',
                   l: str='Paramaribo', s: str='Paramaribo', c: str='SR',
                   mail: str='ca@krishna.sr') -> x509.Name:
        """Create a Certificate Signing Request"""
        # create an X509 Name
        name = x509.Name([
            x509.NameAttribute(x509.NameOID.COMMON_NAME, str(cn)),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, str(o)),
            x509.NameAttribute(x509.NameOID.ORGANIZATIONAL_UNIT_NAME, str(ou)),
            x509.NameAttribute(x509.NameOID.LOCALITY_NAME, str(l)),
            x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, str(s)),
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, str(c)),
            x509.NameAttribute(x509.NameOID.EMAIL_ADDRESS, str(mail)),
            ])
        return name

    def genkey(self) -> rsa.RSAPrivateKey:
        """Create a Certificate Signing Request and corresponding private key"""
        # create the private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend())
        return private_key

    def gencsr(self, name, private_key, is_intermediate=False,
               san: list=['kris.local']) -> x509.CertificateSigningRequest:
        """Create a Certificate Signing Request and corresponding private key"""
        # type checks
        if not (isinstance(private_key, rsa.RSAPrivateKey) or isinstance(private_key, ec.EllipticCurvePrivateKey)):
            raise TypeError('The provided key is not a RSA or ECDSA key')
        if not isinstance(name, x509.Name):
            raise TypeError('The provided name is not a x509.Name')

        # create a signing request
        request = x509.CertificateSigningRequestBuilder().subject_name(
            name
        ).add_extension(
            x509.KeyUsage(digital_signature=True,
                          content_commitment=False,
                          key_encipherment=bool(not is_intermediate),
                          data_encipherment=bool(not is_intermediate),
                          key_agreement=False,
                          key_cert_sign=bool(is_intermediate),
                          crl_sign=bool(is_intermediate),
                          encipher_only=False,
                          decipher_only=False),
            critical=True
        ).add_extension(
            x509.BasicConstraints(ca=bool(is_intermediate), path_length=(0 if bool(is_intermediate) else None)),
            critical=True,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
            critical=False,
        )

        # assign extended usages
        extended_usages = []
        extended_usages.append(x509.oid.ExtendedKeyUsageOID.SERVER_AUTH)
        extended_usages.append(x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH)

        request = request.add_extension(
            x509.ExtendedKeyUsage(extended_usages),
            critical=False
        )

        # assign alternative names
        if (not is_intermediate) and isinstance(san, list) and len(san) > 0:
            alt_names = []
            for alt_name in san:
                alt_names.append(x509.DNSName(str(alt_name)))
            request = request.add_extension(x509.SubjectAlternativeName(alt_names), critical=False)

        # sign the CSR
        request = request.sign(
            private_key,
            hashes.SHA256(),
            default_backend()
        )

        return request

    def signcsr(self, csr, days=90) -> (x509.Certificate):
        """Create a Certificate using the provided certificate signing request"""
        # type checks
        if not isinstance(csr, x509.CertificateSigningRequest):
            raise TypeError('The provided name is not a x509.Name')

        # build the certificate
        builder = x509.CertificateBuilder().subject_name(
            csr.subject
        ).issuer_name(
            self.certificate.subject
        ).public_key(
            csr.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=int(days))
        ).add_extension(
            extension=x509.AuthorityKeyIdentifier.from_issuer_public_key(self.private_key.public_key()),
            critical=False
        )
        for ext in csr.extensions:
            builder = builder.add_extension(ext.value, critical=ext.critical)

        certificate = builder.sign(
            private_key=self.private_key,
            algorithm=hashes.SHA256(),
            backend=default_backend()
        )

        return certificate

    @classmethod
    def createca(cls, path, passphrase: str='passphrase', cn: str='Krishna Root CA', o: str='Krishna Organization',
                 ou: str='Test Department', l: str='Paramaribo', s: str='Paramaribo', c: str='SR',
                 mail: str='ca@krishna.sr', days=365,
                 algorithm: str='RSA') -> (rsa.RSAPrivateKey, x509.Certificate):
        """Create a self-signed certificate that we can use as root for the CA"""

        # we can only create a CA if the files do not exist
        if os.path.exists(path):
            raise ValueError("The given path is already in use")

        # create the X509 objects
        ca = cls(path, load_files=False)
        ca.algorithm = algorithm
        private_key = ca.genkey()
        name = ca.createname(cn, o, ou, l, s, c, mail)

        # create a self-signed root certificate
        certificate = x509.CertificateBuilder().subject_name(
            name
        ).issuer_name(
            name
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=int(days))
        ).add_extension(
            x509.KeyUsage(digital_signature=False,
                          content_commitment=False,
                          key_encipherment=False,
                          data_encipherment=False,
                          key_agreement=False,
                          key_cert_sign=True,
                          crl_sign=True,
                          encipher_only=False,
                          decipher_only=False),
            critical=True
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=1),
            critical=True,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
            critical=False,
        ).sign(private_key, hashes.SHA256(), default_backend())

        # write the files to disk
        write_to_file(path, passphrase, private_key, certificate)

        return private_key, certificate


def write_to_file(path, passphrase, private_key, certificate):
    """Write the cryptographic material to disk"""

    # create the output directory
    if not os.path.exists(path):
        os.mkdir(path)

    # write the files to disk
    filename_key = os.path.join(path, 'key.priv')
    with open(filename_key, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode()),
        ))

    filename_key = os.path.join(path, 'key.pub')
    with open(filename_key, 'wb') as f:
        f.write(private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))

    filename_key = os.path.join(path, 'key.pem')
    with open(filename_key, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    filename_crt = os.path.join(path, 'cert.pem')
    with open(filename_crt, 'wb') as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))

    filename_pass = os.path.join(path, 'global.pass')
    with open(filename_pass, 'w') as f:
        f.write(str(passphrase))


# Command line interface
def run():

    # createca:  createca [2:ca folder] [3:ca password]
    #            python ca.py createca root_ca passphrase
    # readca:    readca [2:ca folder] [3:ca password] [4:output folder]
    #            python ca.py readca root_ca passphrase ca_output
    # createcrt: createcrt [2:ca folder] [3:ca password] [4:output folder] [5:crt password] [7:is_intermediate]
    #            python ca.py createcrt root_ca passphrase child_ca1 password1 True
    #            python ca.py createcrt root_ca passphrase child_ca2 password1 True
    #            python ca.py createcrt child_ca1 password1 web_crt password2 False
    #            python ca.py createcrt child_ca1 password1 api_crt password2 False
    #            python ca.py createcrt child_ca2 password1 client_crt password2 False
    # readcrt:   readcrt [2:ca folder] [3:ca password] [4:crt folder] [5:crt password] [6:output folder]
    #            python ca.py readcrt root_ca passphrase child_crt password crt_output

    print('--- START ---')
    print('Input: ', sys.argv[1:])

    if 'createca' in sys.argv[1]:
        ca_folder = sys.argv[2]
        ca_passphrase = sys.argv[3]
        # create a key and certificate
        private_key, certificate = CertAuthority.createca(ca_folder, ca_passphrase)
        print('Created a certificate authority in', ca_folder)
    elif 'readca' in sys.argv[1]:
        ca_folder = sys.argv[2]
        ca_passphrase = sys.argv[3]
        output_folder = sys.argv[4]

        # read the root certificate
        ca = CertAuthority(ca_folder, ca_passphrase)

        # write the outputs to disk
        write_to_file(output_folder, ca_passphrase, ca.private_key, ca.certificate)
        for ext in ca.certificate.extensions:
            print(ext)
        print('Read a certificate authority from', ca_folder)

    elif 'createcrt' in sys.argv[1]:
        ca_folder = sys.argv[2]
        ca_passphrase = sys.argv[3]
        output_folder = sys.argv[4]
        crt_passphrase = sys.argv[5]
        is_intermediate = sys.argv[6].lower() in ['true', '1', 'y', 'yes']

        # read the root certificate
        ca = CertAuthority(ca_folder, ca_passphrase)

        # create a certificate
        private_key = ca.genkey()
        name = ca.createname(cn='kris.local')
        csr = ca.gencsr(name, private_key, is_intermediate, san=['kris.local', 'www.kris.local', 'api.kris.local'])
        certificate = ca.signcsr(csr)

        # write the outputs to disk
        write_to_file(output_folder, crt_passphrase, private_key, certificate)
        for ext in certificate.extensions:
            print(ext)
        print('Created a certificate in', output_folder)

    elif 'readcrt' in sys.argv[1]:
        print('Not implemented.')

    print('---- END ----')


if __name__ == "__main__":
    run()
