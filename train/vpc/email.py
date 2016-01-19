#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imp
import os
import base64
import sys

import mandrill


from config import *

if os.environ.get("MANDRILL_KEY"):
    mandrill_client = mandrill.Mandrill(os.environ.get('MANDRILL_KEY'))

def email_credentials(conn):
    """Email all user information and credentials listed in USER_FILE"""

    if not os.environ.get("MANDRILL_KEY"):
        print "\nERROR: Required environment variable 'MANDRILL_KEY' not set!\n"
        sys.exit()

    print 'Emailing user information and credentials ...'

    mail = imp.load_source('mail', EMAIL_TEMPLATE)
    with open(USER_FILE) as file:
        for line in file:
            instances = ''
            username = line.split(',')[0].strip()
            email = line.split(',')[1].strip()

            # keyfile
            with open ('/host/share/{0}/{0}-{1}.pem'.format(username, VPC), "r") as f:
                keyfile = base64.b64encode(f.read())
            # ppkfile
            with open ('/host/share/{0}/{0}-{1}.ppk'.format(username, VPC), "r") as f:
                ppkfile = base64.b64encode(f.read())

            # instances
            files = [f for f in os.listdir('/host/share/{0}/'.format(username)) if f.endswith('.txt')]
            for textfile in files:
                with open('/host/share/{0}/{1}'.format(username, textfile)) as f:
                    instances += f.read()
                    instances += '\n'

            try:
                message = {
                    'from_email': mail.from_email,
                    'from_name': mail.from_name,
                    'to': [{'email': email, 'name': username, 'type': 'to'}],
                    'subject': mail.subject,
                    'text': mail.text,
                    'attachments': [
                        {
                            "type": "text/plain",
                            "name": "{0}.pem".format(username),
                            "content": keyfile
                        },
                        {
                            "type": "text/plain",
                            "name": "{0}.ppk".format(username),
                            "content": ppkfile
                        },
                        {
                            "type": "text/plain",
                            "name": "instances.txt",
                            "content": base64.b64encode(instances)
                        }
                    ],
                }

                result = mandrill_client.messages.send(message=message)
                print "Welcome email sent to: '{0}' <{1}> ...".format(username, email)

            except mandrill.Error, e:
                print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
                raise
