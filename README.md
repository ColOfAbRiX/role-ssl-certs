# ssl-certs

Ansible role to create, install, trust and manage [X.509 Certificates](1) (commonly known as SSL/TLS Certificates).

The role tries to be flexible and generic and doesn't want to impose opinionated views on how to manage your PKI. The role has been designed to work as a pipeline and to support as many features as possible and to uniform the way the PKI is created. These are the features of the ssl-certs role:

 - It can create self-signed certificates, including Root Certification Authorities.
 - It supports DSA, RSA and ECDSA keys.
 - It outputs keys and certificates in PEM format (more formats to come).
 - It supports the encryption of the private key with a passphrase.
 - It can create signed certificates from existing or new CA.
 - Or it can just stop at the CSR create and later installation of a certificate.
 - It can create certificate chain files.
 - It can generate multiple certificates with the same private key.
 - If you have existing certificates this role can use them.
 - It can install the certificates in a specific location on the target system.
 - And it can use a local path to store the keys and certificates.
 - It can install the certificates on trust stores (OS dependent).
 - It can use extended SSLv3 attributes.

## Requirements and Dependencies

The role only requires OpenSSL which is installed where required by the role itself.

The OS-level trust of certificate is supported only on CentOS/RedHat 7.

# Description

The role works by using the `ssl_sequence` list of dictionaries as a sequence of entities to create. It will process each entity one at the time and for each one of them it will examine the `key`, `certificate` and `chain` key, one at, the time and create the appropriate files.

The role can use the Ansible local machine both as a store for the produced certificates/keys and a source for files to be installed on the targets. Ansible becomes the single and main source of all data. This use can be turned off using configuration variables.

**NOTE:** All private keys that are kept in a GIT repository must be encrypted with [Ansible vault](2). **Never keep plain text secrets in GIT.**

The [default configuration](defaults/main.yml) file contains a fully working example of how the role can be used to create a root CA, a certificate signed by that CA and a certificate chain with the description of all the options.

## Limitations and known issues

The role only creates certificates in [PEM format](3). PKC#12 is on the plan.

Recreation of existing certificates and keys must be triggered manually with the various options given by the role (like `force_create`).

If the definition of an entity changes the role will not recreate the entity or, in other words, updated of certificate and keys is not supported directly but it can still be achieved forcing recreation.

## Role Variables

The variables are fully documented in the [default configuration](defaults/main.yml) file, including their default values and some examples.
The default values mirror the default BIND configuration for the distribution where it is installed.

| Variable                  | Default                       | Description                                             |
| :---                      | :---                          | :---                                                    |
| `ssl_store_base`          | `../storage/ssl_certificates` | Path on the Ansible server where to store certificate.  |
| `ssl_base`                | dict                          | Default working path on the target machine.             |
| `ssl_key_dir`             | dict                          | Subdirectory of `ssl_base` where to store keys.         |
| `ssl_csr_dir`             | dict                          | Subdirectory of `ssl_base` where to store CSR.          |
| `ssl_crt_dir`             | dict                          | Subdirectory of `ssl_base` where to store certificates. |
| `ssl_sequence`            | `[]`                          | SSL definitions. Objects will be created following this sequence, one after t       he other.|
| `ssl_country`             | `GB`                          | Default OpenSSL value for Country.                      |
| `ssl_state`               | `London`                      | Default OpenSSL value for State.                        |
| `ssl_location`            | `London`                      | Default OpenSSL value for Location.                     |
| `ssl_organization`        | `Example Company`             | Default OpenSSL value for Organization.                 |
| `ssl_organizational_unit` | `IT Operations`               | Default OpenSSL value for Organizational Unit.          |
| `ssl_email`               | `admin@example.com`           | Default OpenSSL value for E-Mail.                       |

The variables `ssl_base`, `ssl_key_dir`, `ssl_csr_dir` and `ssl_crt_dir` are dictionaries that support the keys of the [Ansible file module](4), refer to the [default configuration](defaults/main.yml) for examples.

## Examples

The following example creates a local Root CA and two certificates, with some custom properties for the certificates:

```Yaml
ssl_sequence:
 # Root CA
 - name: root_ca
   key:
     type:                   rsa
     bits:                   4096
   certificate:
     self_signed:            yes
     common_name:            Root CA
     basicConstraints:       'critical, CA:TRUE'
     subjectKeyIdentifier:   'hash'
     authorityKeyIdentifier: 'keyid:always, issuer:always'
     keyUsage:               'critical, cRLSign, digitalSignature, keyCertSign'
     days:                   3653

 # Website signed certificate
 - name: website
   key:
     type:                   rsa
     bits:                   2048
   certificate:
     common_name:            "{{ ansible_fqdn }}"
     alt_names_dns:          [ "internal.example.com" ]
     # Reference the above CA certificate
     signing_key:            root_ca
```

More examples are in the [default configuration](defaults/main.yml) file.

## TODO

In order of priority

* Fetch also CSR files
* Support for PKC#12 format
* Cascade recreation of entities

## License

MIT

## Author Information

Fabrizio Colonna (@ColOfAbRiX)

## Contributors

Issues, feature requests, ideas, suggestions, etc. are appreciated and can be posted in the Issues section.

Pull requests are also very welcome. Please create a topic branch for your proposed changes. If you don't, this will create conflicts in your fork after the merge.

[1]: https://www.wikiwand.com/en/X.509#/Certificates
[2]: https://docs.ansible.com/ansible/latest/vault.html
[3]: https://www.wikiwand.com/en/Privacy-Enhanced_Mail
[4]: https://docs.ansible.com/ansible/latest/modules/file_module.html
