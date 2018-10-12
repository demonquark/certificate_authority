"""
This module contains the Certificate Authority class that handles PKI related functionality.
"""


class CertAuthority(object):
    """represents a CA
    """
    def __init__(self, path):
        """Initializes the CA
        """
        self.path = path
