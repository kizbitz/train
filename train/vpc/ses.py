#!/usr/bin/env python
# -*- coding: utf-8 -*-

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import imp
import os

import boto.ses

from config import *
from util import check_email_template


# TODO: Check for verified email address
# TODO: Add option to verify an email address

def prep_file(path, username):
    """Configure email attachments"""

    attachment = MIMEApplication(open(path, 'rb').read())
    attachment.add_header('Content-Disposition',
                          'attachment',
                          filename='{0}.{1}'.format(username, path.split('.')[1]))

    return(attachment)


def email_credentials():
    """Email all user information and credentials listed in USER_FILE"""

    check_email_template()
    SES_REGION = check_ses_region('SES_REGION')
    SES_FROM_EMAIL = check_env('SES_FROM_EMAIL')
    SES_FROM_NAME = check_env('SES_FROM_NAME', ' ')

    conn = boto.ses.connect_to_region(SES_REGION,
                                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    print 'Emailing user information and credentials ...'
    mail = imp.load_source('mail', EMAIL_TEMPLATE)
    with open(USER_FILE) as file:
        for line in file:
            # defaults
            instances = ''
            mail_body = mail.body
            username = line.split(',')[0].strip()

            # message
            msg = MIMEMultipart()
            msg.preamble = 'Multipart message.\n'
            msg['Subject'] = mail.subject
            msg['From'] = '{0} <{1}>'.format(SES_FROM_NAME, SES_FROM_EMAIL).strip()
            msg['To'] = line.split(',')[1].strip()

            # *.pem and *.ppk files
            msg.attach(prep_file('/host/{0}/users/{1}/{1}-{0}.pem'.format(VPC, username), username))
            msg.attach(prep_file('/host/{0}/users/{1}/{1}-{0}.ppk'.format(VPC, username), username))

            # instance information
            mail_body += "\n---\n\nAWS instances:\n"

            files = [f for f in os.listdir('/host/{0}/users/{1}/'.format(VPC, username)) if f.endswith('.txt')]
            for textfile in files:
                with open('/host/{0}/users/{1}/{2}'.format(VPC, username, textfile)) as f:
                    for line in f:
                        if line.startswith('AWS'):
                            continue
                        else:
                            instances += line

            mail_body += instances
            msg.attach(MIMEText(mail_body))

            try:
                result = conn.send_raw_email(msg.as_string(), source=msg['From'], destinations=msg['To'])
                print "Welcome email sent to: '{0}' <{1}> ...".format(username, msg['To'])
            except:
                print 'Error sending email to: {0}'.format(username, msg['To'])
                raise
