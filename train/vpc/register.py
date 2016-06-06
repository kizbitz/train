#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import string
import sys

from config import *
import ses
import labs
from util import check_email_template
import vpc


def _checks():
    """Requirements"""

    if os.environ.get('USER_FILE'):
        print 'ERROR: USER_FILE environment variable must not be set.'
        sys.exit()
    if os.path.exists('/host/{0}/users.cfg'.format(VPC)):
        os.rename('/host/{0}/users.cfg'.format(VPC), '/host/{0}/users.cfg.register.bak'.format(VPC))
    check_email_template()


def set_username(user):
    """Create username from email"""

    count = 0
    username = user.split('@')[0].lower().strip()

    for c in string.punctuation:
        username = username.replace(c, '')

    basename = username
    while os.path.exists('/host/{0}/users/{1}'.format(VPC, username)):
        count += 1
        username = basename + str(count)

    return username


def welcome_instructions():
    """Provide instructions/reminders when launching"""

    print """
Registration Mode:

- It's recommend to use a custom email template (with no prompts) that sets:
    - from_email, from_name, and subject variables with static entries.
        - See '/home/train/train/templates/email.py'
    - Specify 'EMAIL_TEMPLATE' environment variable with the path to your template

- The welcome message entered below will be shown to each individial before prompting for email.
- To exit registration mode type 'exit' during the email prompt.
"""

def registration(conn, user_vpc, lab):
    """Implements registration mode"""

    _checks()
    welcome_instructions()
    welcome = raw_input('Enter a welcome message: ')

    while True:
        os.system('clear')
        print '\n' + welcome
        current_email = raw_input("\nPlease enter a valid email address (or 'exit' to quit): ")

        if current_email.lower() == 'exit':
            break
        else:

            # don't allow duplicate usernames
            username = set_username(current_email.strip())

            with open('/host/{0}/users.cfg'.format(VPC), 'w') as f:
                f.write(username + ',' + current_email + '\n')
            with open('/host/{0}/registered-users.txt'.format(VPC), 'a') as f:
                f.write(username + ',' + current_email + '\n')

        vpc.create_key_pairs()
        labs.launch_lab(conn, user_vpc, lab)
        ses.email_credentials()

        print '\n'
        print '-' * 35
        print '\nInstances launched successfully ...'
        raw_input("\nPress 'Enter' to continue ")

    # clean up
    if os.path.exists('/host/{0}/users.cfg.register.bak'.format(VPC)):
        os.rename('/host/{0}/users.cfg.register.bak'.format(VPC), '/host/{0}/users.cfg'.format(VPC))
