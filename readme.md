# request-review-cert.py

*request-review-cert.py* issues a bash command for a request to a a dogtag PKI server, extracts the necessary information (request ID) from the request, and then issues a bash review command to automatically approve the client certificate within a local instance.


## Steps to configure DS and CA servers on a VM and run the script

### Setting up the Virtual Machine:

I created a virtual machine with 2 cores and 20 GB disk space, using Virtual Box hypervisor, and installed Fedora Workstation 36 using an ISO file from the following link: https://getfedora.org/en/workstation/download/

After the Fedora OS installation completed, removed the ISO, used the following commands in the terminal to make sure all necessary packages were installed and up to date:

First I had to make sure the root user password was set, or root user could not be logged into, by using *"sudo passwd root"*. Logged in as the root user using the *"su"* command with password and issued *"dnf update"*. Some of the java packages were causing a conflict for creating the LDAP server once I reached that point, so used the *"dnf list --installed | grep java"* and *"dnf remove <package>"* commands to fix the issue.

###### A full console log of package installations, including for the DS and CA, can be seen in the file *packages_installation.log*

### DS and CA Instances Set-up:
    
Sent *"dnf install -y 389-ds-base"* and *"dnf install -y dogtag-pki"* commands to install the necessary packages for the directory server and certificate authority server. To make my VM hostname match with the examples from the quick start guide, sent "hostname pki.example.com" command to change the hostname followed by a reboot.

###### A shortened console log of the DS and CA package installation can be seen in the file *DS and PKI install only.log*

Issued the following commands the same as written in the dogtagspki wiki:

1. Created and input into the ds.inf file:

*"dscreate create-template ds.inf"*

then

_"sed -i \
    -e "s/;instance_name = .*/instance_name = localhost/g" \
    -e "s/;root_password = .*/root_password = Secret.123/g" \
    -e "s/;suffix = .*/suffix = dc=example,dc=com/g" \
    -e "s/;create_suffix_entry = .*/create_suffix_entry = True/g" \
    -e "s/;self_sign_cert = .*/self_sign_cert = False/g" \
    ds.inf"_

2. Created the instance from the ds.inf file:

*"dscreate from-file ds.inf"*

3. Created the PKI Subtree:


*"ldapadd -H ldap://$HOSTNAME -x -D "cn=Directory Manager" -w Secret.123 << EOF
dn: dc=pki,dc=example,dc=com
objectClass: domain
dc: pki
EOF"*

4. For creating the CA server, the command "pkispawn" was sent, and all default settings were kept for the installation. After this, sent "exit" to stop using the root account.

###### A console log of the DS and CA instance creation can be seen in the file *ds_and_pki_instances.log*

### Manual Test

1. The *"pki -c Secret.123 client-init"* command was sent to make sure the client database was initialized with a blank slate during testing. 
2. Issued the client certificate request using the *"pki -c Secret.123 client-cert-request uid=testuser"* command. For the first request, a prompt was issued to confirm trust for the CA server.
3. The returned request ID could be used in the *"pki -u caadmin ca-cert-request-review <request id>"* command to issue the review request. After getting past the password and action prompts, the request was approved with a status confirmation.

### Automated Test:

Using the sys, subprocess, and pexpect (needed to be pip installed) modules, a request to the CA is issued and the input was stored into a string. Using the split method, the request ID is extracted from the string and stored into a variable. This variable is in an f-string for the review request, and after the prompt selections are entered, the review process completes. See the following output in the command line after running the script:

----------------------------------------------------------------------------------------

[taylorherring@pki ~]$ python request-review-cert.py

[taylorherring@pki ~]$ pki -u caadmin ca-cert-request-review 0x19

Enter Password: 

--------------------------------

Retrieved certificate request 25

--------------------------------

  Request ID: 0x19

  Profile: Manual User Dual-Use Certificate Enrollment

  Type: enrollment

  Status: pending



  Key Generation:

    cert_request_type: pkcs10

    cert_request: -----BEGIN CERTIFICATE REQUEST-----

MIICXzCCAUcCAQAwGjEYMBYGCgmSJomT8ixkAQEMCHRlc3R1c2VyMIIBIjANBgkqhkiG9w0BAQEF

AAOCAQ8AMIIBCgKCAQEAz0vPWhFqQHRdEOUa1KqGPK/HyhObHXBwk8K40cQP+jvq1BnFsoJO2glS

8ObZLmdmrqzrs+cqnBj+Yb18fMu9Al0LJsIRBLbX08WBHzanblMwofvS2W4iuJYwOQuryfTobErZ

fl0eqUYNRzuI8OESP3aiDtyBBNe8AwiOzgKX6cnJ8zqL7E205OrjQkm6D/23lYVgwkKuwEV4mv9h

DTVqa5S1aBATxdjezx0vCNYNMI+C2mqA7FV11QQgWkRNYE8yX4AkvD/smWT057MvEY+3yfTULHvW

OV3iCXSzsd9oGnGAOP0C2Lzzdl18qRVVOPNMyoGf5y7T188VpSHVICb1rwIDAQABoAAwDQYJKoZI

hvcNAQELBQADggEBAETMPIgGzyUbZP+emySU4y3AgCwUR2BVZ1STn1zZFGI62M7YqavOtVeTaxjr

8RDEe2U64QeaVSq0JYxxomVe2mFtmt5G5ndK4IFMIFx158c0JuWN6nnFATN1s19/9jbblxHowxDp

3ejcx/GMKhKvmmBrQdPklMtBS3skUkN//lcaxhKvvO3dp/Pq8A4pkEoCyeAlUohmcQeF4m8L9FP7

vB18R3cU7muXycUZ8hsIJmfXvxyT2bZOz6clxhQuZhhODodr+tKbKe37ifGc8GKnY7S95xTB65vj

zWm9npk5CuZAhD4VrJC/H7nkgpYTNjg2Pq65vSYYTLT7QkHKpS8bb0M=

-----END CERTIFICATE REQUEST-----



  Subject Name:

    sn_uid: testuser



  Requestor Information:

    none



Action (approve/reject/cancel/update/validate/assign/unassign): approve

-------------------------------

Approved certificate request 25

-------------------------------

  Request ID: 0x19

  Type: enrollment

  Request Status: complete

  Operation Result: success

  Certificate ID: 0x11

[taylorherring@pki ~]$ 


----------------------------------------------------------------------------------------


##### A more detailed log of the script output can be seen in the file *automation_script_console.log*. 