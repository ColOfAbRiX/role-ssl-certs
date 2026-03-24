# ssl-certs

Ansible role to create, install, trust and manage [X.509 Certificates](1) (commonly known as SSL/TLS
Certificates).

The role tries to be flexible and generic and doesn't want to impose opinionated views on how to
manage your PKI. The role has been designed to work as a pipeline and to support as many features as
possible and to uniform the way the PKI is created.

## Quick Start

To get started quickly with this role:

1. Add the role to your playbook:

   ```yaml
   - hosts: servers
     roles:
       - role: ssl-certs
         ssl_sequence:
           - name: example_cert
             key:
               type: rsa
               bits: 2048
             certificate:
               common_name: "{{ ansible_fqdn }}"
               self_signed: yes
               days: 365
   ```

2. Run your playbook:

   ```bash
   ansible-playbook -i inventory playbook.yml
   ```

3. Your certificate will be created at the paths defined by the role variables.

For more complex setups, see the detailed Examples section below.

## Installation

There are multiple ways to include this role in your playbook:

### Option 1: Using requirements.yml (recommended)

Create a `requirements.yml` file with the following content:

```yaml
- name: ssl-certs
  src: https://github.com/yourusername/ansible-ssl-certs.git
  scm: git
  version: master  # or specify a version tag
```

Then install the role with:

```bash
ansible-galaxy install -r requirements.yml
```

### Option 2: Manual Installation

Clone the repository directly into your roles directory:

```bash
git clone https://github.com/yourusername/ansible-ssl-certs.git roles/ssl-certs
```

### Option 3: Direct Include

You can also include the role directly in your playbook without prior installation:

```yaml
- hosts: servers
  roles:
    - role: /path/to/roles/ssl-certs
```

## Features

The ssl-certs role provides the following features:

- It can install and trust certificates on the system
- It can create self-signed certificates, including Root Certification Authorities
- It supports DSA, RSA and ECDSA keys
- It outputs keys in PEM format and certificates in PEM, DER or JKS format (more formats to come)
- It supports the encryption of the private key with a passphrase
- It can create signed certificates from existing or new CA
- Or it can just stop at the CSR create and later installation of a certificate
- It can create certificate chain files
- It can generate multiple certificates with the same private key
- If you have existing certificates this role can use them
- It can install the certificates in a specific location on the target system
- And it can use a local path to store the keys and certificates
- It can install the certificates on trust stores (OS dependent)
- It can use extended SSLv3 attributes

## OS Compatibility

The role should work on most Unix-like operating systems, but the following functionality varies by
platform:

- **Certificate Trust Store Integration**:
  - Full support on CentOS/RedHat 7+ (using `update-ca-trust`)
  - Limited support on Debian/Ubuntu (using `update-ca-certificates`)
  - Windows/Cygwin support via custom trust store location
  - Other distributions may require manual trust configuration

- **Package Dependencies**:
  - The role automatically installs the required OpenSSL packages for your distribution
  - Java is required only if using JKS format conversion

## Format Conversion

The role supports converting certificates to multiple formats:

- **PEM**: Default format for all certificates (standard text-based format)
- **DER**: Binary format suitable for certain applications
- **JKS**: Java KeyStore format for Java applications

To use format conversion, specify the desired format(s) in the certificate definition:

```yaml
certificate:
  # DER format conversion
  der:
    convert: yes
    force_create: yes
  # JKS format conversion
  jks:
    convert: yes
    keystore: /path/to/keystore.jks
    storepass: changeit
```

### Format Conversion Use Cases

- **DER format**: Useful for Microsoft Windows environments or applications that specifically require
  binary certificate formats
- **JKS format**: Essential for Java-based applications such as Tomcat, Jetty, or other Java
  application servers that need certificates in their keystores

## Requirements and Dependencies

The role has the following requirements:

- **OpenSSL**: Automatically installed by the role if not present
- **Java** (optional): Required only if using JKS format conversion
- **Python OpenSSL bindings**: Installed by the role if not present
- **Ansible 2.2.0 or higher**: Required for the cryptographic modules used by this role

The role handles dependencies automatically by installing the required packages for your specific
distribution.

## Description

The role works by using the `ssl_sequence` list of dictionaries as a sequence of entities to create.
It will process each entity one at a time and for each one of them it will examine the `key`,
`certificate` and `chain` key, one at a time and create the appropriate files.

The role can use the Ansible local machine both as a store for the produced certificates/keys and a
source for files to be installed on the targets. Ansible becomes the single and main source of all
data. This use can be turned off using configuration variables.

**NOTE:** All private keys that are kept in a GIT repository must be encrypted with [Ansible
vault](2). **Never keep plain text secrets in GIT.**

The [default configuration](defaults/main.yml) file contains a fully working example of how the role
can be used to create a root CA, a certificate signed by that CA and a certificate chain with the
description of all the options.

## Role Workflow

The role follows a specific workflow when executing:

1. **Pre-checks**: Verifies that the required dependencies are available and the configuration is
   valid.
2. **Entity Management**: Processes each entity in the `ssl_sequence` list:
   - **Private Key Creation**: Generates private keys according to the specified parameters.
   - **Certificate Creation**: Creates certificates or certificate signing requests (CSRs).
   - **Chain Creation**: Builds certificate chains if configured.
3. **Format Conversion**: Converts certificates to other formats (DER, JKS) if requested.
4. **Trust Management**: Installs certificates to the system's trust store if specified.

This pipeline approach allows for flexible certificate management and automation of the entire PKI
lifecycle.

## Certificate Renewal and Revocation

The role doesn't directly support certificate revocation lists (CRLs) or the OCSP protocol. However,
you can implement a renewal process using the following approaches:

### Certificate Renewal

To renew certificates, you can:

1. Set the `force_create` option to `yes` for the entities you want to renew
2. Keep the same entity name to ensure file paths remain consistent
3. Adjust the `days` parameter to set the new validity period

Example renewal workflow:

```yaml
ssl_sequence:
  - name: web_server
    force_create: yes  # Force renewal
    key:
      type: rsa
      bits: 2048
    certificate:
      common_name: "{{ ansible_fqdn }}"
      signing_key: root_ca
      days: 365  # New validity period
```

### Handling Revocation

While the role doesn't create CRLs, you can:

1. Create a new CA if your root CA is compromised
2. Re-issue certificates using the new CA
3. Update certificate chains to include the new CA
4. Deploy the updated certificates to all services

## Integration with Web Servers

While the role focuses on certificate creation and management, it can be easily integrated with
common web servers. Here are some examples:

### Apache Integration

```yaml
- name: Generate Apache certificate
  hosts: web_servers
  roles:
    - role: ssl-certs
      ssl_sequence:
        - name: apache_cert
          key:
            type: rsa
            bits: 2048
            # Set owner to Apache user
            owner: www-data
            group: www-data
            mode: '0400'
          certificate:
            common_name: "{{ ansible_fqdn }}"
            alt_names_dns: ["www.example.com", "example.com"]
            self_signed: yes
            days: 365
            # Set owner to Apache user
            owner: www-data
            group: www-data
            mode: '0444'

- name: Configure Apache
  hosts: web_servers
  tasks:
    - name: Configure SSL in Apache
      template:
        src: ssl.conf.j2
        dest: /etc/apache2/sites-enabled/ssl.conf
      notify: restart apache
```

### Nginx Integration

```yaml
- name: Generate Nginx certificate
  hosts: web_servers
  roles:
    - role: ssl-certs
      ssl_sequence:
        - name: nginx_cert
          key:
            type: rsa
            bits: 2048
            # Set owner to Nginx user
            owner: nginx
            group: nginx
            mode: '0400'
          certificate:
            common_name: "{{ ansible_fqdn }}"
            alt_names_dns: ["www.example.com", "example.com"]
            self_signed: yes
            days: 365
            # Set owner to Nginx user
            owner: nginx
            group: nginx
            mode: '0444'

- name: Configure Nginx
  hosts: web_servers
  tasks:
    - name: Configure SSL in Nginx
      template:
        src: nginx_ssl.conf.j2
        dest: /etc/nginx/conf.d/ssl.conf
      notify: restart nginx
```

## Limitations and known issues

The role only creates certificates in [PEM format](3) by default, with optional conversion to DER
and JKS formats. PKC#12 format is on the plan.

Recreation of existing certificates and keys must be triggered manually with the various options
given by the role (like `force_create`).

If the definition of an entity changes the role will not recreate the entity or, in other words,
updates of certificates and keys are not supported directly but can still be achieved by forcing
recreation.

## Role Variables

The variables are fully documented in the [default configuration](defaults/main.yml) file, including
their default values and some examples. The default values mirror the default BIND configuration for
the distribution where it is installed.

| Variable                  | Default                       | Description                                                                           |
| :---                      | :---                          | :---                                                                                  |
| `ssl_base`                | dict                          | Default working path on the target machine.                                           |
| `ssl_chain_dir`           | dict                          | Subdirectory of `ssl_base` where to store certificate chains.                         |
| `ssl_country`             | `GB`                          | Default OpenSSL value for Country.                                                    |
| `ssl_crt_dir`             | dict                          | Subdirectory of `ssl_base` where to store certificates.                               |
| `ssl_csr_dir`             | dict                          | Subdirectory of `ssl_base` where to store CSR.                                        |
| `ssl_email`               | `admin@example.com`           | Default OpenSSL value for E-Mail.                                                     |
| `ssl_key_dir`             | dict                          | Subdirectory of `ssl_base` where to store keys.                                        |
| `ssl_location`            | `London`                      | Default OpenSSL value for Location.                                                   |
| `ssl_organization`        | `Example Company`             | Default OpenSSL value for Organization.                                               |
| `ssl_organizational_unit` | `IT Operations`               | Default OpenSSL value for Organizational Unit.                                        |
| `ssl_sequence`            | `[]`                          | SSL definitions. Objects will be created following this sequence, one after the other.|
| `ssl_state`               | `London`                      | Default OpenSSL value for State.                                                      |
| `ssl_store_path`          | `../storage/ssl_certificates` | Path on the Ansible server where to store certificate.                                |

The variables `ssl_base`, `ssl_key_dir`, `ssl_csr_dir`, `ssl_crt_dir`, and `ssl_chain_dir` are
dictionaries that support the keys of the [Ansible file module](4), refer to the [default
configuration](defaults/main.yml) for examples.

## Examples

The following example creates a local Root CA and two certificates, with some custom properties for
the certificates:

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

## Path Hierarchy

The role uses a hierarchical approach to file paths, allowing for flexible configuration at
different levels:

1. **Global base path**: Defined by `ssl_store_path` (for local storage) and `ssl_base.path` (for
   target system)
2. **Entity path**: Can be overridden per entity with `ssl_sequence.<entity>.store_path` or
   `ssl_sequence.<entity>.path`
3. **Object type path**: Defined by `ssl_key_dir.name`, `ssl_csr_dir.name`, `ssl_crt_dir.name`, and
   `ssl_chain_dir.name`
4. **Object path**: Can be further customized with `ssl_sequence.<entity>.<object>.store_path` or
   `ssl_sequence.<entity>.<object>.path`

Each level can override the previous, with more specific paths taking precedence. The paths are
joined using Python's `os.path.join`.

### Path Hierarchy Examples

**Example 1: Default Paths**

With default configuration:
```yaml
ssl_store_path: ../file_store/ssl_certificates
ssl_base:
  path: /tmp/ssl_certs
ssl_key_dir:
  name: key
ssl_crt_dir:
  name: crt
```

A certificate would be stored at:
- Local path: `../file_store/ssl_certificates/crt/example.crt`
- Remote path: `/tmp/ssl_certs/crt/example.crt`

**Example 2: Custom Entity Path**

With custom entity path:
```yaml
ssl_sequence:
  - name: custom_cert
    path: /etc/custom_certs
    store_path: ../backups/certs
    certificate:
      common_name: example.com
      self_signed: yes
```

This certificate would be stored at:
- Local path: `../backups/certs/crt/custom_cert.crt`
- Remote path: `/etc/custom_certs/crt/custom_cert.crt`

**Example 3: Custom Object Path**

With custom object path:
```yaml
ssl_sequence:
  - name: web_cert
    certificate:
      common_name: example.com
      self_signed: yes
      path: /etc/nginx/ssl
```

This certificate would be stored at:
- Local path: `../file_store/ssl_certificates/crt/web_cert.crt`
- Remote path: `/etc/nginx/ssl/web_cert.crt`

## Security Considerations

- **Private Key Protection**: Always encrypt private keys stored in repositories using [Ansible
  vault](2)
- **Passphrase Encryption**: Use the `encryption` and `passphrase` options to protect sensitive
  private keys
- **File Permissions**: The role sets appropriate permissions on directories and files (e.g.,
  private keys default to mode '0700')
- **Least Privilege**: When deploying certificates to services, use specific user/group permissions
  to limit access
- **Key Length**: Use appropriate key lengths (RSA: 2048+ bits, ECDSA: prime256v1 or stronger)
- **Certificate Validity**: Limit certificate validity periods (1-2 years for standard certs, 5-10
  years for root CAs)
- **Secure Storage**: Use secure storage for your Ansible vault password
- **Secure Passphrases**: Use strong, unique passphrases for encrypted keys
- **Audit Trail**: Keep records of certificate creation, renewal, and revocation

## Troubleshooting

Common issues and solutions:

1. **Certificate Not Trusted**:
   - Check if the `trust: yes` option is set
   - Verify your OS is supported for trust store integration
   - For unsupported distributions, manually install the certificate in the system trust store
   - On Debian/Ubuntu, run `update-ca-certificates` manually after installation
   - On RedHat/CentOS, run `update-ca-trust extract` manually after installation

2. **JKS Conversion Fails**:
   - Ensure Java is installed on the target system
   - Check that the keystore path is writable by the specified user
   - Verify that the Java keytool command is available in the PATH
   - Try specifying the full path to the keytool command
   - Check the storepass value is correct if accessing an existing keystore

3. **Permission Issues**:
   - Check the permissions set in the `ssl_base`, `ssl_key_dir`, `ssl_crt_dir`, etc. dictionaries
   - Ensure the user running Ansible has sufficient privileges
   - For system paths, make sure to run Ansible with sufficient privileges (sudo)
   - Check SELinux contexts if running on a system with SELinux enabled

4. **Certificate Not Being Updated**:
   - Use the `force_create: yes` option to recreate certificates and keys
   - Check if the files exist with different owners/permissions that prevent overwriting
   - Verify that Ansible has write permissions to both local and remote paths

5. **Invalid Certificate or Key Format**:
   - Check OpenSSL version compatibility between systems
   - Ensure the certificate and key files aren't corrupted
   - Verify the parameters passed to OpenSSL are correct for your OpenSSL version

6. **Certificate Chain Issues**:
   - Ensure certificates are listed in the correct order in the chain
   - Verify all certificates in the chain are valid and not expired
   - Check for missing intermediate certificates

7. **SSL Certificate Common Name Mismatch**:
   - Ensure the common_name matches the actual hostname or domain
   - Consider using alt_names_dns for multi-domain certificates
   - For wildcard certificates, format should be `*.example.com`

## TODO

In order of priority:

- Fetch also CSR files
- Support for PKC#12 format
- Cascade recreation of entities
- Add certificate revocation capabilities
- Support for OCSP stapling configuration
- Add automatic certificate renewal
- Support for hardware security modules (HSMs)
- Integration with Let's Encrypt for automatic public certificates

## License

MIT

## Author Information

Fabrizio Colonna (@ColOfAbRiX)

## Contributors

Issues, feature requests, ideas, suggestions, etc. are appreciated and can be posted in the Issues
section.

Pull requests are also very welcome. Please create a topic branch for your proposed changes. If you
don't, this will create conflicts in your fork after the merge.

[1]: https://www.wikiwand.com/en/X.509#/Certificates
[2]: https://docs.ansible.com/ansible/latest/vault.html
[3]: https://www.wikiwand.com/en/Privacy-Enhanced_Mail
[4]: https://docs.ansible.com/ansible/latest/modules/file_module.html
