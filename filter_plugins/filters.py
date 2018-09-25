#!/usr/bin/python
#
# Fabrizio Colonna <colofabrix@tin.it> - 19/09/2018
#

import os


def cert_files_in_chain(values, certs_list, base_path=""):
    """
    Find the entries in the SSL Sequence that are referenced by a certificate list
    """
    result = []

    for cert_name in certs_list:
        # To accept an entry it must contain a certificate definition and its
        # name must be in the certs_list
        cert_entries = filter(
            lambda c: 'certificate' in c and c['name'] == cert_name,
            values
        )
        cert_entries = map(
            lambda c: "%s/%s.%s" % (c.get('crt_base', base_path), c['name'], 'crt'),
            cert_entries
        )
        result.extend(cert_entries)

    return result


class FilterModule(object):
    """ Ansible core jinja2 filters """
    def filters(self):
        return {
            'cert_files_in_chain': cert_files_in_chain,
        }

# vim: ft=python:ts=4:sw=4