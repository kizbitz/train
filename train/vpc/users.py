#!/usr/bin/env python
# -*- coding: utf-8 -*-

import util

from config import *

POLICY = '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "ec2:*",
      "Effect": "Allow",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "elasticloadbalancing:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "cloudwatch:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "autoscaling:*",
      "Resource": "*"
    },
    {
      "Action": "iam:*",
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}'''


def create_user(conn, user):
    conn.create_user(user)
    conn.put_user_policy(user, 'train', POLICY)
    info = conn.create_access_key(user)

    print "\n'{0}' user created succesfully ...\n".format(user)
    print "Username: {0}".format(info.user_name)
    print "Access Key ID: {0}".format(info.access_key_id)
    print "Secret Access Key: {0}\n".format(info.secret_access_key)


def delete_user(conn, user):
    pass


def list_users(conn):
    pass
