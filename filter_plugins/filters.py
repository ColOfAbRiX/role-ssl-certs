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

    for entry in values:
        # To accept an entry it must contain a certificate definition and its
        # name must be in the certs_list
        if 'certificate' in entry and entry['name'] in certs_list:
            cert_file = "%s/%s.%s" % (
                entry.get('crt_base', base_path),
                entry['name'],
                'crt'
            )
            result.append(cert_file)

    return result


class FilterModule(object):
    """ Ansible core jinja2 filters """
    def filters(self):
        return {
            'cert_files_in_chain': cert_files_in_chain,
        }

# vim: ft=python:ts=4:sw=4