#!/usr/bin/python
#
# Fabrizio Colonna <colofabrix@tin.it> - 19/09/2018
#

import os


def certificates_in_chain(values, certs_list):
    """
    Find the entries in the SSL Sequence that are referenced by a certificate list
    """
    result = []

    for entry in values:
        # To accept an entry it must contain a certificate definition and its
        # name must be in the certs_list
        if 'certificate' in entry and entry.get('name', '') in certs_list:
            result.append(entry)

    return result


def build_file_list(values, base_path):
    """
    Given a certificate list, it build the list of their actual files
    """
    result = []

    for entry in values:
        result.append(
            os.path.join(entry.get('csr_base', base_path), entry.name, '.crt')
        )

    return result


class FilterModule(object):
    """ Ansible core jinja2 filters """
    def filters(self):
        return {
            'certificates_in_chain': certificates_in_chain,
            'build_file_list': build_file_list,
        }

# vim: ft=python:ts=4:sw=4