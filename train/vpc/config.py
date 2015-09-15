#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import amis


def check_env(env, default=None):
    """Check/Set environment variables"""

    if not os.environ.get(env) and not default:
        print "Error: {0} environment variable not set".format(variable)
        sys.exit()

    return os.environ.get(env, default)


def check_user_file(user_file):
    """Check/create USER_FILE"""

    if user_file:
        return user_file
    elif os.path.exists('/host/users.cfg'):
        return '/host/users.cfg'
    else:
        with open('/tmp/trainer.txt', 'w') as f:
            f.write(TRAINER + '\n')
        return '/tmp/trainer.txt'


# Required environment variables
# ==============================

# Trainer name. Used to tag VPC, Security Groups, etc...
TRAINER = check_env('TRAINER')

# AWS region, id, and key
AWS_REGION = check_env('AWS_REGION')
AWS_ACCESS_KEY_ID = check_env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = ('AWS_SECRET_ACCESS_KEY')


# Optional environment variables
# ==============================

# Root lab directory
LAB_DIR = check_env('LAB_DIR', '/home/train/train/labs/')

# Full path to user configuration file
USER_FILE = check_user_file(os.environ.get('USER_FILE'))

# Tag for VPC, labs, instances, etc...
TRAIN_TAG = check_env('TRAIN_TAG', 'train')


# Other
# =====

# AWS AMI dictionary
AMIS = getattr(amis, AWS_REGION.upper().replace('-', '_'))

# AWS IAM Profile
IAM_PROFILE = TRAINER + '-{0}'.format(TRAIN_TAG)

# AWS Gateway
IGW = TRAINER + '-{0}-igw'.format(TRAIN_TAG)

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
NETWORK_ACL = TRAINER + '-{0}-network-acl'.format(TRAIN_TAG)

# AWS Route Table
ROUTE_TABLE = TRAINER + '-{0}-route-table'.format(TRAIN_TAG)

# AWS VPC CIDR
VPC_CIDR = "10.0.0.0/16"

# AWS VPC Tag
VPC_TAG = TRAINER + '-{0}'.format(TRAIN_TAG)

# AWS Zones
ZONES=['a', 'b', 'c', 'd', 'e', 'f']
