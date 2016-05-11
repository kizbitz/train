#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import string
import util

from boto.iam.connection import IAMConnection

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
      "Effect": "Allow",
      "Action": "ses:*",
      "Resource": "*"
    },
    {
      "Action": "iam:*",
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}'''


def generate_password():
    """The best password generator ever!"""

    uppercase = (random.choice(string.letters) for _ in range(4))
    lowercase = (random.choice(string.letters) for _ in range(4))
    numbers = (str(random.randint(10, 99)) for _ in range(3))
    punctuation = (random.choice("!#$%&()*+-_.:;<>=") for _ in range(3))

    p = list(''.join(uppercase) + ''.join(lowercase) + \
             ''.join(numbers) + ''.join(punctuation))
    random.shuffle(p)

    return ''.join(p)


def create_user(conn, user):
    conn.create_user(user)
    conn.put_user_policy(user, 'train', POLICY)
    info = conn.create_access_key(user)

    pword = None
    if util.yn_prompt('Allow user to log into the AWS Console?'):
        pword = generate_password()
        conn.create_login_profile(user, pword)

    print "\n'{0}' user created succesfully ...\n".format(user)
    print "Username: {0}".format(info.user_name)
    if pword:
        print "Password: {0}".format(pword)
    print "Access Key ID: {0}".format(info.access_key_id)
    print "Secret Access Key: {0}\n".format(info.secret_access_key)


def delete_user(conn, user):

    if util.yn_prompt("Are you sure you want to delete user: '{0}'?".format(user)):

        all = conn.get_all_user_policies(user)
        policies = all.list_user_policies_response.list_user_policies_result.policy_names
        for policy in policies:
            conn.delete_user_policy(user, policy)

        all = conn.get_all_access_keys(user)
        keys = all.list_access_keys_response.list_access_keys_result.access_key_metadata
        for key in keys:
            conn.delete_access_key(key.access_key_id, user)

        try:
            profile = conn.get_login_profiles(user)
        except:
            profile = None

        if profile:
            conn.delete_login_profile(user)

        conn.delete_user(user)

        print "'{0}' AWS user deleted ...".format(user)
    else:
        print "Delete cancelled ..."


def list_users(conn):
    conn = IAMConnection()
    users = conn.get_all_users()

    print "\nCurrent AWS user accounts:\n"
    for user in users.list_users_result.users:
        print "- {0}".format(user.user_name)
    print ""
