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

# #  Checks Section  # #

def check_sequence_names_present(sequence):
    """
    Checks that the names of entities are all present
    """
    entity_names = map(lambda x: 'name' in x, sequence)
    return {
        'result': any(entity_names),
        'message': "All entries in ssl_sequence must have a name."
    }


def check_sequence_names_uniqe(sequence):
    """
    Checks that the names of entities are all unique
    """
    entity_names = [x['name'] for x in sequence]
    return {
        'result': len(entity_names) == len(set(entity_names)),
        'message': "All names of entries in ssl_sequence must be unique."
    }


def check_sequence_signing_type(sequence):
    """
    Checks that only one of signin_key or self_signed is present in the entry
    """
    return {
        'result': True,
        'message': ""
    }


def check_sequence_signing_keys(sequence):
    """
    Checks that all the signing_keys referenced by a certificate are present,
    that there exists only one and that it appears before that entity.
    """

    # Extract signing keys name of non-self signed certificates
    entity_certs = []
    for e in sequence:
        if 'certificate' in e and 'signing_key' in e['certificate']:
            entity_certs.append({
                'name': e['name'],
                'signing_key': e['certificate']['signing_key']
            })

    return {
        'result': True,
        'message': "",
        'data': entity_certs
    }


def check_sequence_generating_keys(sequence):
    """
    Checks that all the generating_keys referenced by a certificate are present
    and appear before that entity.
    """
    entity_certs = [x['certificate'] for x in sequence if 'certificate' in x]
    return {
        'result': True,
        'message': ""
    }


class FilterModule(object):
    """ Ansible core jinja2 filters """
    def filters(self):
        return {
            'cert_files_in_chain': cert_files_in_chain,
            'check_sequence_names_present': check_sequence_names_present,
            'check_sequence_names_uniqe': check_sequence_names_uniqe,
            'check_sequence_signing_type': check_sequence_signing_type,
            'check_sequence_signing_keys': check_sequence_signing_keys,
            'check_sequence_generating_keys': check_sequence_generating_keys,
        }

# vim: ft=python:ts=4:sw=4