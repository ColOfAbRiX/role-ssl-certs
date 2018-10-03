#!/usr/bin/python
#
# Fabrizio Colonna <colofabrix@tin.it> - 19/09/2018
#


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


def check_sequence_names_present(sequence):
    """
    Checks that the names of entities are all present
    """
    result = any(map(lambda x: 'name' in x, sequence))
    if not result:
        return {
            'result': False,
            'message': "All entries in ssl_sequence must have a name."
        }
    return {
        'result': True,
        'message': "All entries have a defined name."
    }


def check_sequence_names_uniqe(sequence):
    """
    Checks that the names of entities are all unique
    """
    entity_names = [x['name'] for x in sequence]
    result = len(entity_names) == len(set(entity_names))
    if not result:
        return {
            'result': False,
            'message': "All names of entries in ssl_sequence must be unique."
        }
    return {
        'result': True,
        'message': "All entry names are unique."
    }


def check_sequence_signing_type(sequence):
    """
    Checks that only one of signing_key or self_signed is present in the entry
    """
    for entity in sequence:
        # Check only if the entity has a defined certificate
        if 'certificate' not in entity:
            continue
        cert = entity['certificate']

        # Check the keys are not present at the same time
        if 'signing_key' in cert and 'self_signed' in cert:
            return {
                'result': False,
                'message': ("The certificate '%s' can't define signing_key and self_signed at the "
                            "same time.") % entity['name']
            }

    return {
        'result': True,
        'message': "All certificates have a correct private key attribute."
    }


def check_private_keys_helper(sequence, key_type):
    """
    Checks the validity of the references to private keys
    """
    prev_entities = []

    # Scan all entities once
    for entity in sequence:
        # Check only if the entity has a defined certificate
        if 'certificate' not in entity:
            continue

        if key_type in entity['certificate']:
            referenced_key = entity['certificate'][key_type]

            # Look for the signing_key definition in the scanned entities
            signing_entity = filter(lambda x: x['name'] == referenced_key, prev_entities)
            if len(signing_entity) != 1:
                return {
                    'result': False,
                    'message': ("The %s entity '%s' referenced by certificate '%s' is not defined "
                                "or it doesn't appear before the certificate itself in ssl_sequence"
                                ".") % (key_type, referenced_key, entity['name']),
                    'data': signing_entity
                }
            signing_entity = signing_entity[0]

            # Look that the signing_entity actually has a key attribute defined
            if 'key' not in signing_entity:
                return {
                    'result': False,
                    'message': ("The %s entity '%s' referenced by certificate '%s' must define a "
                                "'key' attribute.") % (key_type, referenced_key, entity['name']),
                    'data': signing_entity
                }

        elif 'self_signed' in entity['certificate']:
            # If a certificate is self_signed, it must defined they key itself
            if 'key' not in entity:
                return {
                    'result': False,
                    'message': "The self_signed certificate '%s' must define a 'key' attribute." %
                               entity['name'],
                    'data': signing_entity
                }

        # Remember what came before
        prev_entities.append(entity)

    return {
        'result': True,
        'message': "All %s appear to be good." % key_type
    }


def check_sequence_generating_keys(sequence):
    """
    Checks that all the generating_keys referenced by a certificate are present
    and appear before that entity.
    """
    return check_private_keys_helper(sequence, 'generating_key')


def check_sequence_signing_keys(sequence):
    """
    Checks that all the signing_keys referenced by a certificate are present,
    that there exists only one and that it appears before that entity.
    """
    return check_private_keys_helper(sequence, 'signing_key')


class FilterModule(object):
    """ Ansible core jinja2 filters """
    def filters(self):
        return {
            'cert_files_in_chain': cert_files_in_chain,
            'check_sequence_names_present': check_sequence_names_present,
            'check_sequence_names_uniqe': check_sequence_names_uniqe,
            'check_sequence_signing_type': check_sequence_signing_type,
            'check_sequence_generating_keys': check_sequence_generating_keys,
            'check_sequence_signing_keys': check_sequence_signing_keys,
        }

# vim: ft=python:ts=4:sw=4
