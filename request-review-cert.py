#!/usr/bin/python3
import subprocess
import pexpect
import sys

request_output = subprocess.run(['pki', '-c', 'Secret.123', 'client-cert-request', 'uid=testuser'], capture_output=True, text=True, input='y').stdout

# The split method is called for the request_output string below, to extract the request ID needed for the ca-cert-request-review command
request_id = request_output.split("Request ID: ")[1].split("\n")[0]


# since using subprocess became more complicated for interacting with prompts, used the pexpect module to send the review request and enter input to the 2 prompts
review_process = pexpect.spawn('/bin/bash', encoding='utf-8')

# assigned the logfile_read attribute to sys.stdout to automatically display the CLI output for the review process
review_process.logfile_read = sys.stdout
review_process.delaybeforesend = 0.5

# request and prompt inputs:
review_process.sendline(f'pki -u caadmin ca-cert-request-review {request_id}')
review_process.expect('Enter Password:')
review_process.sendline('Secret.123')
review_process.expect('Action')
review_process.sendline('approve')
review_process.expect('Certificate ID')
