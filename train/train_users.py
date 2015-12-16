#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Train-Users: AWS CLI IAM/User Managment"""

import argparse
import sys

import boto

from vpc.config import *
import vpc.users as users

conn = boto.connect_iam(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

# configure parser
parser = argparse.ArgumentParser(description='Train: AWS CLI IAM/User Management')

parser.add_argument('-c', metavar='<user>',
                    help='Create IAM/User',
                    required=False)

parser.add_argument('-d', metavar='<user>',
                    help='Delete AWS user',
                    required=False)

parser.add_argument('-l',
                    help='List all users',
                    action='store_true', required=False)

args = parser.parse_args()


def process():
    """Execute command/flags"""

    if args.c:
        users.create_user(conn, args.c)
    if args.d:
        users.delete_user(conn, args.d)
    if args.l:
        users.list_users(conn)


if __name__ == '__main__':
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    process()
