#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import string
import sys

from config import *
import email
import labs
import vpc


def _checks():
    """Requirements"""

    if os.environ.get('USER_FILE'):
        print 'ERROR: USER_FILE environment variable must not be set.'
        sys.exit()
    if os.path.exists('/host/users.cfg'):
        os.rename('/host/users.cfg', '/host/users.cfg.register.bak')


def set_username(user):
    """Create username from email"""

    username = user.split('@')[0].lower()

    for c in string.punctuation:
        username = username.replace(c, '')

    if os.path.exists('/host/share/{0}'.format(username)):
        count = 1
        username = username + str(count)
        while os.path.exists('/host/share/{0}'.format(username)):
            count += 1
            username = username + str(count)

    return username


def welcome_instructions():
    """Provide instructions/reminders when launching"""

    print """
Registration Mode:

- It's recommend to use a custom email template (with no prompts) that sets:
    - from_email, from_name, and subjet variables with static entries.
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
        current_email = raw_input("\nPlease enter a valid email address: ")

        if current_email.lower() == 'exit':
            break
        else:

            # don't allow duplicate usernames
            username = set_username(current_email.strip())

            with open('/tmp/user.txt', 'w') as f:
                f.write(username + ',' + current_email + '\n')
            with open('/host/registered-users.txt', 'a') as f:
                f.write(username + ',' + current_email + '\n')

        vpc.create_key_pairs()
        labs.launch_lab(conn, user_vpc, lab)
        email.email_credentials(conn)

        print '\n'
        print '-' * 35
        print '\nInstances launched successfully ...'
        raw_input("\nPress 'Enter' to continue ")

    # clean up
    if os.path.exists('/host/users.cfg.register.bak'):
        os.rename('/host/users.cfg.register.bak', '/host/users.cfg')
    with open('/tmp/user.txt', 'w') as f:
        f.write(os.environ['TRAINER'] + '\n')

