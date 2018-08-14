# ssl-certs

Ansible role to create, install, trust and manage SSL Certificates.

The role can:

 - create self-signed certificate, including Root Certification Authorities;
 - create signed certificates and full certificate chains;
 - install the certificates in a specific location on the target system;
 - trust globally the certificates.
 - use extended SSLv3 attributes.

## Requirements

The role requires RHEL/CentOS 7 to work. The creation of certificate most probably works on other platforms but it hasn't been tested and the role has been locked for RHEL/CentOS only.

OpenSSL is also required to be installed on the target system.

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
