#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import amis


def check_env(env, default=None):
    """Check/Set environment variables"""

    if not os.environ.get(env) and not default:
        print "Error: '{0}' environment variable not set".format(env)
        sys.exit()

    return os.environ.get(env, default)


def check_user_file(VPC, user_file):
    """Check/create USER_FILE"""

    if user_file:
        return user_file
    elif os.path.exists('/host/{0}/users.cfg'.format(VPC)):
        return '/host/{0}/users.cfg'.format(VPC)
    else:
        if not os.path.exists('/host/{0}'.format(VPC)):
            os.makedirs('/host/{0}'.format(VPC))
        with open('/host/{0}/users.cfg'.format(VPC), 'w') as f:
            f.write(TRAINER + '\n')
        return '/host/{0}/users.cfg'.format(VPC)


def get_email_template(VPC, template):
    """Check EMAIL_TEMPLATE"""

    if template:
        return template
    elif os.path.exists('/host/{0}/email.py'.format(VPC)):
        return '/host/{0}/email.py'.format(VPC)
    else:
        return '/home/train/train/templates/email.py'


def check_ses_region(env):
    """Check/Set SES_REGION environment variable"""

    # Available SES Regions: http://docs.aws.amazon.com/general/latest/gr/rande.html#ses_region
    SES_REGIONS = ['us-east-1', 'us-west-2', 'eu-west-1']

    if not os.environ.get(env):
        print "Error: '{0}' environment variable not set".format(env)
        sys.exit()
    else:
        if not os.environ.get(env) in SES_REGIONS:
            print "Error: The '{0}' region specified is not one of the available SES regions".format(os.environ.get(env))
            print "       See: http://docs.aws.amazon.com/general/latest/gr/rande.html#ses_region"
            sys.exit()
        else:
            return os.environ.get(env)


# Required environment variables
# ==============================

# Trainer name. Used to tag VPC, Security Groups, etc...
TRAINER = check_env('TRAINER')

# AWS region, id, and key
AWS_REGION = check_env('AWS_REGION')
AWS_ACCESS_KEY_ID = check_env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = check_env('AWS_SECRET_ACCESS_KEY')

# Optional environment variables
# ==============================

# Tag for VPC, labs, instances, etc...
VPC = check_env('VPC', 'train')

# Root lab directory
LAB_DIR = check_env('LAB_DIR', '/home/train/train/labs/')

# Full path to user configuration file
USER_FILE = check_user_file(VPC, os.environ.get('USER_FILE'))

# Email Template
EMAIL_TEMPLATE = get_email_template(VPC, os.environ.get('EMAIL_TEMPLATE'))

# Note: Checked in ses.py
# SES_REGION
# SES_FROM_EMAIL
# SES_FROM_NAME

# Other
# =====

# AWS AMI dictionary
AMIS = getattr(amis, AWS_REGION.upper().replace('-', '_'))

# AWS IAM Profile
IAM_PROFILE = TRAINER + '-{0}'.format(VPC)

# AWS Gateway
IGW = TRAINER + '-{0}-igw'.format(VPC)

# IAM Policy
POLICY = """{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeAvailabilityZones",
        "ec2:DescribeTags"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}"""


# AWS Network ACL
NETWORK_ACL = TRAINER + '-{0}-network-acl'.format(VPC)

# AWS Route Table
ROUTE_TABLE = TRAINER + '-{0}-route-table'.format(VPC)

# AWS VPC CIDR
VPC_CIDR = "10.0.0.0/16"

# AWS VPC Tag
VPC_TAG = TRAINER + '-{0}'.format(VPC)

# AWS Zones
ZONES=['a', 'b', 'c', 'd', 'e', 'f']
