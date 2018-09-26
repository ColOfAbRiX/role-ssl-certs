# ssl-certs

Ansible role to create, install, trust and manage [X.509 Certificates](1) (commonly known as SSL/TLS Certificates).

These are the features of the ssl-certs role:

 - It can create self-signed certificates, including Root Certification Authorities.
 - It can create signed certificates from existing or new CA.
 - It can create certificate chains files.
 - If you have existing certificates this role can use them.
 - It supports DSA, RSA and ECDSA keys.
 - It outputs keys and certificates in PEM format.
 - It supports the encryption of the private key with a passphrase.
 - It can install the certificates in a specific location on the target system.
 - It can trust globally the certificates (OS dependent).
 - It can use extended SSLv3 attributes.
 - It can use the Ansible inventory to store the keys and certificates.

[1]: https://www.wikiwand.com/en/X.509#/Certificates

## Requirements

The role only requires OpenSSL installed on the system.

The global trusting of the certificate requires CentOS/RedHat 7.

# Description

The role works by using the `ssl_sequence` list of dictionaries as a sequence of elements to create. It will process each entry one at the time and for each one of them it will examine the `key`, `certificate` and `chain` elements, one at, the time and create the files.

The role can use the Ansible local code to store all the produced certificates and key such that Ansible becomes the single and main source of all data. This use can be turned off using configuration variables.

**NOTE:** All private keys that are kept in the repository must be encrypted with Ansible vault.

The [default configuration](defaults/main.yml) file contains a fully working example of how the role can be used to create a root CA, a certificate signed by that CA and a certificate chain with the description of all the options.

## Role Variables

The variables are fully documented in the [default configuration](defaults/main.yml) file, including their default values and some examples.
The default values mirror the default BIND configuration for the distribution where it is installed.

| Variable           | Default                       | Description                                             |
| :---               | :---                          | :---                                                    |
| `ssl_store_base`   | `../storage/ssl_certificates` | Path on the Ansible server where to store certificate.  |
| `ssl_base`         | dict                          | Default working path on the target machine.             |
| `ssl_key_dir`      | dict                          | Subdirectory of `ssl_base` where to store keys.         |
| `ssl_csr_dir`      | dict                          | Subdirectory of `ssl_base` where to store CSR.          |
| `ssl_crt_dir`      | dict                          | Subdirectory of `ssl_base` where to store certificates. |
| `ssl_sequence`     | `[]`                          | SSL definitions. Objects will be created following this sequence, one after the other.|
| `ssl_country`      | `GB`                          | Default OpenSSL value for Country.                      |
| `ssl_state`        | `London`                      | Default OpenSSL value for State.                        |
| `ssl_location`     | `London`                      | Default OpenSSL value for Location.                     |
| `ssl_organization` | `Example Company`             | Default OpenSSL value for Organization.                 |
| `ssl_organizational_unit` | `IT Operations`        | Default OpenSSL value for Organizational Unit.          |
| `ssl_email`        | `admin@example.com`           | Default OpenSSL value for E-Mail.                       |

The variables `ssl_base`, `ssl_key_dir`, `ssl_csr_dir` and `ssl_crt_dir` are dictionaries, refer to the [default configuration](defaults/main.yml) for their full description.

## Dependencies

The role has not dependencies.

## Examples

The following example creates a local Root CA and two certificates, with some custom properties for the certificates:

```Yaml
ssl_sequence:
 # Root CA
 - name: root_ca
   # If using custom paths, they must exist beforehand
   key_base: /tmp/key
   csr_base: /tmp/csr
   crt_base: /tmp/crt
   key:
     bits:                   4096
   certificate:
     self_signed:            yes
     common_name:            Root CA
     organizational_unit:    Example Security Office
     # Installs the certificate on the system
     trust:                  yes
     # SSL v3 extensions. Default is to omit these values
     basicConstraints:       'critical, CA:TRUE'
     subjectKeyIdentifier:   'hash'
     authorityKeyIdentifier: 'keyid:always, issuer:always'
     keyUsage:               'critical, cRLSign, digitalSignature, keyCertSign'

 # Website signed certificate
 - name: website
   # It forces the creation of a new key and certificate on the machine
   force_create: yes
   # It gives priority to the key that is stored remotely versus the one stored
   # on the local repository
   force_remote: yes
   key:
     bits:                   2048
     owner:                  nginx
     group:                  nginx
   certificate:
     common_name:            "{{ ansible_fqdn }}"
     alt_names_dns:          ["internal.example.com"]
     # Reference the above CA certificate
     signing_key:            root_ca
     digest:                 sha1
     days:                   90
```

## License

MIT

## Author Information

Fabrizio Colonna (@ColOfAbRiX)

## Contributors

Issues, feature requests, ideas, suggestions, etc. are appreciated and can be posted in the Issues section.

Pull requests are also very welcome. Please create a topic branch for your proposed changes. If you don't, this will create conflicts in your fork after the merge.
